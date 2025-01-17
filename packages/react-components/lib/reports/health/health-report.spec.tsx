import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { TestLocalizationProvider } from '../../test/locale';
import { getHealthLogs, reportConfigProps } from '../utils.spec';
import { HealthReport } from './health-report';

const getLogsPromise = async () => getHealthLogs();

it('smoke test', async () => {
  await waitFor(() => {
    render(<HealthReport getLogs={getLogsPromise} />);
  });
});

it('doesn`t shows the table when logs list is empty', async () => {
  await waitFor(() => {
    render(<HealthReport getLogs={async () => await []} />);
  });

  expect(screen.queryByText('Health')).toBeFalsy();
});

it('calls the retrieve log function when the button is clicked', async () => {
  const getLogsPromiseMock = jasmine.createSpy();
  const getLogsPromise = async () => {
    getLogsPromiseMock();
    return getHealthLogs();
  };
  render(<HealthReport getLogs={getLogsPromise} {...reportConfigProps} />, {
    wrapper: TestLocalizationProvider,
  });
  expect(screen.getByRole('button', { name: /Retrieve Logs/i })).toBeTruthy();
  userEvent.click(screen.getByRole('button', { name: /Retrieve Logs/i }));
  expect(getLogsPromiseMock).toHaveBeenCalled();
});
