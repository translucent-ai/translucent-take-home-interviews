# Take‑Home (2‑3 hrs) – Platform Engineer

**Objective:** Extend a partially built Terraform module by adding minimal GuardDuty alerting and writing a design note.

## Provided

* `main.tf` – EKS cluster already configured with IRSA.
* `variables.tf`, `outputs.tf`
* CI workflow (`.github/workflows/tf.yml`) that runs `terraform fmt`, `validate`, `tflint`.
* `test/cluster_test.go` – basic Terratest (passes).

## Your Tasks (should fit in ~2 hrs of Terraform work)

1. **Add GuardDuty detector + event rule + SNS topic** in `guardduty.tf`. Target: alerts land in SNS.
2. Expose `sns_topic_arn` via `outputs.tf`.
3. Update `examples/simple/main.tf` so `terraform plan` shows your new resources.
4. Fill out **`DESIGN_TRADOFFS.md`** (≤1 page) on isolation, cost, alert routing.

No need to integrate PagerDuty—onsite we’ll discuss options.

## Quick start

```bash
cd examples/simple
terraform init
terraform plan -var='region=us-east-1' -var='cluster_name=demo' -var='vpc_id=vpc-123' -var='subnet_ids=["subnet-abc"]'
```
