#!/usr/bin/env python3
"""
Baseline Pipeline Monitor - A simple pipeline monitoring system

This is a basic implementation that candidates should enhance with:
- Better pipeline health tracking
- Intelligent alerting with severity levels
- Anomaly detection for performance issues
- Efficient data structures for high-volume processing
- Dashboard capabilities for visualization
"""

import argparse
import json
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
import statistics


class PipelineStatus(Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class AlertSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Alert:
    def __init__(self, pipeline_id: str, severity: AlertSeverity, message: str, 
                 team: str, timestamp: datetime):
        self.pipeline_id = pipeline_id
        self.severity = severity
        self.message = message
        self.team = team
        self.timestamp = timestamp
    
    def to_dict(self):
        return {
            'pipeline_id': self.pipeline_id,
            'severity': self.severity.value,
            'message': self.message,
            'team': self.team,
            'timestamp': self.timestamp.isoformat()
        }


class PipelineExecution:
    def __init__(self, execution_id: str, pipeline_id: str, status: str, 
                 start_time: str, end_time: str, duration: int, 
                 records_processed: int, team: str):
        self.execution_id = execution_id
        self.pipeline_id = pipeline_id
        # Handle unknown statuses gracefully
        try:
            self.status = PipelineStatus(status)
        except ValueError:
            self.status = PipelineStatus.UNKNOWN
        self.start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        self.end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None
        self.duration = duration if duration is not None else 0  # seconds
        self.records_processed = records_processed if records_processed is not None else 0
        self.team = team


class PipelineMonitor:
    """Basic pipeline monitoring system with room for improvement."""
    
    def __init__(self):
        self.executions = []
        self.pipeline_metrics = defaultdict(lambda: {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'avg_duration': 0,
            'avg_records_processed': 0,
            'last_execution': None,
            'team': None,
            'durations': [],  # Store recent durations for anomaly detection
            'records_processed_history': [],  # Store recent records processed
            'status_history': [],  # Store recent statuses
            'execution_times': []  # Store execution timestamps
        })
        self.alerts = []
        self.alert_history = defaultdict(list)  # Track recent alerts to prevent spam
        self.anomaly_thresholds = {
            'success_rate': 80,  # Alert if below 80%
            'duration_std_dev': 2,  # Alert if duration > 2 std deviations
            'throughput_decrease': 50  # Alert if throughput drops by 50%
        }
        
    def load_executions(self, data_file: str) -> None:
        """Load pipeline execution data from file."""
        with open(data_file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    execution = PipelineExecution(
                        execution_id=data['execution_id'],
                        pipeline_id=data['pipeline_id'],
                        status=data['status'],
                        start_time=data['start_time'],
                        end_time=data['end_time'],
                        duration=data['duration'],
                        records_processed=data['records_processed'],
                        team=data['team']
                    )
                    self.executions.append(execution)
                    self._update_pipeline_metrics(execution)
    
    def _update_pipeline_metrics(self, execution: PipelineExecution) -> None:
        """Update metrics for a pipeline based on execution data."""
        metrics = self.pipeline_metrics[execution.pipeline_id]
        metrics['total_executions'] += 1
        metrics['team'] = execution.team
        
        if execution.status == PipelineStatus.SUCCESS:
            metrics['successful_executions'] += 1
        elif execution.status == PipelineStatus.FAILED:
            metrics['failed_executions'] += 1
        
        # Update execution history (keep last 100 executions)
        MAX_HISTORY = 100
        
        if execution.duration and execution.duration > 0:
            metrics['durations'].append(execution.duration)
            if len(metrics['durations']) > MAX_HISTORY:
                metrics['durations'].pop(0)
            metrics['avg_duration'] = statistics.mean(metrics['durations'])
        
        if execution.records_processed and execution.records_processed > 0:
            metrics['records_processed_history'].append(execution.records_processed)
            if len(metrics['records_processed_history']) > MAX_HISTORY:
                metrics['records_processed_history'].pop(0)
            metrics['avg_records_processed'] = statistics.mean(metrics['records_processed_history'])
        
        metrics['status_history'].append(execution.status)
        if len(metrics['status_history']) > MAX_HISTORY:
            metrics['status_history'].pop(0)
        
        metrics['execution_times'].append(execution.start_time)
        if len(metrics['execution_times']) > MAX_HISTORY:
            metrics['execution_times'].pop(0)
        
        metrics['last_execution'] = execution.start_time
    
    def get_pipeline_health(self, pipeline_id: Optional[str] = None) -> Dict[str, Any]:
        """Get health status for a specific pipeline or all pipelines."""
        if pipeline_id:
            if pipeline_id not in self.pipeline_metrics:
                return {'error': f'Pipeline {pipeline_id} not found'}
            
            metrics = self.pipeline_metrics[pipeline_id]
            success_rate = (metrics['successful_executions'] / metrics['total_executions'] * 100) if metrics['total_executions'] > 0 else 0
            
            return {
                'pipeline_id': pipeline_id,
                'success_rate': success_rate,
                'total_executions': metrics['total_executions'],
                'failed_executions': metrics['failed_executions'],
                'avg_duration': metrics['avg_duration'],
                'avg_records_processed': metrics['avg_records_processed'],
                'last_execution': metrics['last_execution'].isoformat() if metrics['last_execution'] else None,
                'team': metrics['team']
            }
        else:
            # Return health for all pipelines
            health_summary = {}
            for pid, metrics in self.pipeline_metrics.items():
                success_rate = (metrics['successful_executions'] / metrics['total_executions'] * 100) if metrics['total_executions'] > 0 else 0
                health_summary[pid] = {
                    'success_rate': success_rate,
                    'total_executions': metrics['total_executions'],
                    'team': metrics['team']
                }
            return health_summary
    
    def detect_anomalies(self) -> List[Alert]:
        """Detect anomalies in pipeline executions using statistical analysis."""
        anomalies = []
        
        for pipeline_id, metrics in self.pipeline_metrics.items():
            if metrics['total_executions'] < 5:
                continue  # Skip pipelines with insufficient data

            # 1. Success Rate Analysis
            success_rate = (metrics['successful_executions'] / metrics['total_executions']) * 100
            if success_rate < self.anomaly_thresholds['success_rate']:
                severity = AlertSeverity.HIGH if success_rate < 50 else AlertSeverity.MEDIUM
                self._add_alert(anomalies, pipeline_id, severity,
                               f"Low success rate: {success_rate:.1f}%", metrics['team'])

            # 2. Duration Analysis
            if len(metrics['durations']) >= 5:
                avg_duration = statistics.mean(metrics['durations'])
                std_duration = statistics.stdev(metrics['durations'])
                latest_duration = metrics['durations'][-1]
                
                if std_duration > 0:  # Prevent division by zero
                    z_score = abs(latest_duration - avg_duration) / std_duration
                    if z_score > self.anomaly_thresholds['duration_std_dev']:
                        severity = AlertSeverity.HIGH if z_score > 3 else AlertSeverity.MEDIUM
                        self._add_alert(anomalies, pipeline_id, severity,
                                       f"Abnormal duration: {latest_duration}s (z-score: {z_score:.2f})",
                                       metrics['team'])

            # 3. Throughput Analysis
            if len(metrics['records_processed_history']) >= 5:
                avg_throughput = statistics.mean(metrics['records_processed_history'])
                latest_throughput = metrics['records_processed_history'][-1]
                if avg_throughput > 0:  # Prevent division by zero
                    throughput_drop = ((avg_throughput - latest_throughput) / avg_throughput) * 100
                    if throughput_drop > self.anomaly_thresholds['throughput_decrease']:
                        self._add_alert(anomalies, pipeline_id, AlertSeverity.HIGH,
                                       f"Severe throughput drop: {throughput_drop:.1f}% decrease",
                                       metrics['team'])

            # 4. Failure Pattern Analysis
            recent_statuses = metrics['status_history'][-5:]
            if len(recent_statuses) == 5:
                failure_count = sum(1 for status in recent_statuses 
                                  if status == PipelineStatus.FAILED)
                if failure_count >= 3:
                    self._add_alert(anomalies, pipeline_id, AlertSeverity.CRITICAL,
                                   f"Repeated failures: {failure_count}/5 recent executions failed",
                                   metrics['team'])
                
            # 5. Report Generation Pattern Analysis
            if 'report' in pipeline_id.lower():
                recent_times = metrics['execution_times'][-10:]
                if len(recent_times) >= 2:
                    time_diffs = [(t2 - t1).total_seconds() / 3600  # Convert to hours
                                 for t1, t2 in zip(recent_times[:-1], recent_times[1:])]
                    avg_interval = statistics.mean(time_diffs) if time_diffs else 24
                    
                    # Check if report generation is delayed
                    if avg_interval > 25:  # More than 25 hours between reports
                        self._add_alert(anomalies, pipeline_id, AlertSeverity.HIGH,
                                       f"Report generation delayed: {avg_interval:.1f} hours between runs",
                                       metrics['team'])
                    
                    # Check for missing reports
                    last_run = metrics['last_execution']
                    if last_run:
                        hours_since_last = (datetime.now(last_run.tzinfo) - last_run).total_seconds() / 3600
                        if hours_since_last > avg_interval * 1.5:  # 50% longer than usual
                            self._add_alert(anomalies, pipeline_id, AlertSeverity.HIGH,
                                           f"Missing report: {hours_since_last:.1f} hours since last generation",
                                           metrics['team'])
        
        return anomalies

    def _add_alert(self, anomalies: List[Alert], pipeline_id: str, severity: AlertSeverity,
                   message: str, team: str) -> None:
        """Add alert with deduplication to prevent alert spam."""
        # Check for similar recent alerts
        recent_alerts = self.alert_history[pipeline_id]
        current_time = datetime.now()
        
        # Remove alerts older than 1 hour
        recent_alerts = [alert for alert in recent_alerts
                        if (current_time - alert.timestamp).total_seconds() < 3600]
        
        # Check for similar alerts in the last hour
        for alert in recent_alerts:
            if alert.severity == severity and alert.message == message:
                return  # Skip duplicate alert
        
        # Add new alert
        alert = Alert(pipeline_id=pipeline_id, severity=severity,
                     message=message, team=team, timestamp=current_time)
        anomalies.append(alert)
        recent_alerts.append(alert)
        self.alert_history[pipeline_id] = recent_alerts
    
    def get_team_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics aggregated by team."""
        team_metrics = defaultdict(lambda: {
            'total_pipelines': 0,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'avg_success_rate': 0
        })
        
        for pipeline_id, metrics in self.pipeline_metrics.items():
            team = metrics['team']
            team_metrics[team]['total_pipelines'] += 1
            team_metrics[team]['total_executions'] += metrics['total_executions']
            team_metrics[team]['successful_executions'] += metrics['successful_executions']
            team_metrics[team]['failed_executions'] += metrics['failed_executions']
        
        # Calculate average success rates
        for team, metrics in team_metrics.items():
            if metrics['total_executions'] > 0:
                metrics['avg_success_rate'] = (metrics['successful_executions'] / metrics['total_executions']) * 100
        
        return dict(team_metrics)
    
    def get_performance_trends(self, pipeline_id: str, days: int = 7) -> Dict[str, Any]:
        """Get detailed performance trends for a pipeline over the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        # Make cutoff_date timezone-aware to match execution times
        cutoff_date = cutoff_date.replace(tzinfo=self.executions[0].start_time.tzinfo) if self.executions else cutoff_date
        
        recent_executions = [
            exec for exec in self.executions 
            if exec.pipeline_id == pipeline_id and exec.start_time >= cutoff_date
        ]
        
        if not recent_executions:
            return {'error': f'No executions found for {pipeline_id} in the last {days} days'}
        
        # Group executions by day for trend analysis
        daily_metrics = defaultdict(lambda: {
            'executions': 0, 'successes': 0, 'failures': 0,
            'durations': [], 'records': [], 'throughput': []
        })
        
        for exec in recent_executions:
            day_key = exec.start_time.date().isoformat()
            daily_metrics[day_key]['executions'] += 1
            
            if exec.status == PipelineStatus.SUCCESS:
                daily_metrics[day_key]['successes'] += 1
            elif exec.status == PipelineStatus.FAILED:
                daily_metrics[day_key]['failures'] += 1
                
            if exec.duration > 0:
                daily_metrics[day_key]['durations'].append(exec.duration)
            if exec.records_processed > 0:
                daily_metrics[day_key]['records'].append(exec.records_processed)
                if exec.duration > 0:
                    daily_metrics[day_key]['throughput'].append(
                        exec.records_processed / exec.duration
                    )
        
        # Calculate overall statistics
        durations = [exec.duration for exec in recent_executions if exec.duration > 0]
        success_count = sum(1 for exec in recent_executions if exec.status == PipelineStatus.SUCCESS)
        records = [exec.records_processed for exec in recent_executions if exec.records_processed > 0]
        
        # Calculate daily averages and trends
        daily_trends = {}
        for day, metrics in daily_metrics.items():
            daily_trends[day] = {
                'total_executions': metrics['executions'],
                'success_rate': (metrics['successes'] / metrics['executions'] * 100) if metrics['executions'] > 0 else 0,
                'avg_duration': statistics.mean(metrics['durations']) if metrics['durations'] else 0,
                'avg_records': statistics.mean(metrics['records']) if metrics['records'] else 0,
                'avg_throughput': statistics.mean(metrics['throughput']) if metrics['throughput'] else 0
            }
        
        trend_data = {
            'pipeline_id': pipeline_id,
            'success_rate': (success_count / len(recent_executions)) * 100 if recent_executions else 0,
            'avg_duration': statistics.mean(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'total_executions': len(recent_executions),
            'trend_data': [
                {
                    'date': day,
                    'success_rate': metrics['success_rate'],
                    'avg_duration': metrics['avg_duration'],
                    'throughput': metrics['avg_throughput']
                } for day, metrics in sorted(daily_trends.items())
            ],
            'days_analyzed': days
        }
        
        # Add additional stats to help with anomaly detection
        if durations:
            trend_data['duration_std_dev'] = statistics.stdev(durations)
        if records:
            trend_data['avg_records_per_execution'] = statistics.mean(records)
            trend_data['total_records'] = sum(records)
        
        return trend_data
    
    def query(self, query_type: str, **kwargs) -> Any:
        """Execute a query on the pipeline data."""
        if query_type == "pipeline_health":
            return self.get_pipeline_health(kwargs.get('pipeline_id'))
        elif query_type == "anomalies":
            return [alert.to_dict() for alert in self.detect_anomalies()]
        elif query_type == "team_metrics":
            return self.get_team_metrics()
        elif query_type == "performance_trends":
            return self.get_performance_trends(kwargs.get('pipeline_id', ''), kwargs.get('days', 7))
        elif query_type == "total_executions":
            return len(self.executions)
        else:
            return f"Unknown query: {query_type}"


def main():
    parser = argparse.ArgumentParser(description='Monitor data pipeline executions')
    parser.add_argument('--data-file', required=True, help='Path to pipeline execution data file')
    parser.add_argument('--query', required=True, 
                       choices=['pipeline_health', 'anomalies', 'team_metrics', 'performance_trends', 'total_executions'],
                       help='Type of analysis to perform')
    parser.add_argument('--pipeline-id', help='Specific pipeline ID for targeted queries')
    parser.add_argument('--days', type=int, default=7, help='Number of days for trend analysis')
    
    args = parser.parse_args()
    
    monitor = PipelineMonitor()
    monitor.load_executions(args.data_file)
    
    kwargs = {}
    if args.pipeline_id:
        kwargs['pipeline_id'] = args.pipeline_id
    if args.days:
        kwargs['days'] = args.days
    
    result = monitor.query(args.query, **kwargs)
    
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result)


if __name__ == "__main__":
    main()
