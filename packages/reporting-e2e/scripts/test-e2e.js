const concurrently = require('concurrently');
const { execSync } = require('child_process');

process.env.BUILD_PATH = process.env.BUILD_PATH || '../reporting-e2e/build';
process.env.REACT_APP_REPORTING_SERVER =
  process.env.REACT_APP_REPORTING_SERVER || 'http://localhost:8002';
process.env.E2E_REPORTING_SERVER = process.env.E2E_REPORTING_SERVER || 'http://localhost:8003';
process.env.E2E_REPORTING_URL = process.env.E2E_REPORTING_URL || 'http://localhost:5000';

execSync('npm --prefix ../reporting run build', { stdio: 'inherit' });

// wrap in double quotes to support args with spaces
const wdioArgs = process.argv
  .slice(2)
  .map((arg) => `"${arg}"`)
  .join(' ');

const services = [];

// eslint-disable-next-line no-eval
if (!eval(process.env.E2E_NO_REPORTING)) {
  services.push('serve build');
}
// eslint-disable-next-line no-eval
if (!eval(process.env.E2E_NO_REPORTING_SERVER)) {
  services.push('npm run start:reporting-server');
}

concurrently([...services, `wdio ${wdioArgs}`], {
  killOthers: ['success', 'failure'],
  successCondition: 'first',
})
  .then(
    function onSuccess(/* exitInfo */) {
      // This code is necessary to make sure the parent terminates
      // when the application is closed successfully.
      process.exit();
    },
    function onFailure(/* exitInfo */) {
      // This code is necessary to make sure the parent terminates
      // when the application is closed because of a failure.
      process.exit();
    },
  )
  .catch((e) => {
    console.error(e);
    process.exitCode = -1;
  });
