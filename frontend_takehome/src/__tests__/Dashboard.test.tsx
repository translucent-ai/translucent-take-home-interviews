import { render, screen } from '@testing-library/react';
import DenialChart from '../components/DenialChart';

test('renders chart title', () => {
  // TODO: make this pass once DenialChart is implemented
  render(<DenialChart data={[]} />);
  const title = screen.getByText(/Denial Breakdown/i);
  expect(title).toBeInTheDocument();
});
