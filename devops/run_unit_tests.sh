#!/usr/bin/env bash


###test##
###test2###
###test3###
set -e
REPO_DIR=${1:-/workspace/Gan-Shmuel---Green-team}

log() {
    echo "[UNIT-TESTS $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Running unit tests in parallel..."

#run billing unit tests in background
if [ -d "$REPO_DIR/billing-service/tests" ]; then
    log "Installing billing-service dependencies..."
    pip install -r "$REPO_DIR/billing-service/requirements.txt" --break-system-pacages -q 2>/dev/null || true
    log "Starting billing unit tests..."
    (
        set +e
        cd "$REPO_DIR/billing-service"
        pytest tests/ -v > /tmp/billing_test_output.log 2>&1
        echo $? > /tmp/billing_test_result
    ) &
    BILLING_PID=$!
else
    log "No unit tests found for billing-service, skipping..."
    echo "0" > /tmp/billing_test_result
    echo "No tests found" > /tmp/billing_test_output.log
fi

#run weight unit tests in backgroud
if [ -d "$REPO_DIR/weight-service/tests" ]; then
    log "Installing weight-service dependencies..."
    pip install -r "$REPO_DIR/billing-service/requirements.txt" --break-system-packages -q 2>/dev/null || true 
    log "Starting weight unit tests..."
    (
        set +e
        cd "$REPO_DIR/weight-service"
        pytest tests/ -v > /tmp/weight_test_output.log 2>&1
        echo $? > /tmp/weight_test_result
    ) &
    WEIGHT_PID=$!
else
    log "No unit tests found for weight-service, skipping..."
    echo "0" > /tmp/weight_test_result
    echo "No tests found" > /tmp/weight_test_output.log
fi

#wait for both to complete
if [ -n "$BILLING_PID" ]; then
    wait "$BILLING_PID"
fi
if [ -n "$WEIGHT_PID" ]; then
    wait "$WEIGHT_PID"
fi

#check results
BILLING_EXIT=$(cat /tmp/billing_test_result)
WEIGHT_EXIT=$(cat /tmp/weight_test_result)

log "Billing tests exit code: $BILLING_EXIT"
log "Weight tests exit code: $WEIGHT_EXIT"

#check if any failed
if [ "$BILLING_EXIT" -ne 0 ] || [ "$WEIGHT_EXIT" -ne 0 ]; then
    log "Unit tests failed"

    FAILURE_REPORT=""

    if [ "$BILLING_EXIT" -ne 0 ]; then
        FAILURE_REPORT="$FAILURE_REPORT
===========BILLING SERVICE FAILURES==========
$(tail -50 /tmp/billing_test_output.log)
"
    fi

    if [ "$WEIGHT_EXIT" -ne 0 ]; then
        FAILURE_REPORT="$FAILURE_REPORT
============WEIGHT SERVICE FAILURES==========
$(tail -50 /tmp/weight_test_output.log)
"
    fi

    echo "$FAILURE_REPORT"

    echo "$FAILURE_REPORT" > /tmp/unit_test_failure_report.txt

    rm -f /tmp/billing_test_result /tmp/weight_test_result
    rm -f /tmp/billing_test_output.log /tmp/weight_test_output.log

    exit 1
fi

log "All unit tests passed!"

rm -f /tmp/billing_test_result /tmp/weight_test_result
rm -f /tmp/billing_test_output.log /tmp/weight_test_output.log

exit 0