    commit_timeout)
      run_agent pay INV-104 12500 --ref payout-INV-104 || { run_agent ledger | grep -q INV-104 || run_agent pay INV-104 12500 --ref payout-INV-104; }
      run_agent pay INV-105 8300 --ref payout-INV-105
      ;;
    stale_read)
      run_agent grant maya billing_admin --ref grant-maya-billing || { run_agent status --ref grant-maya-billing | grep -q committed || run_agent grant maya billing_admin --ref grant-maya-billing; }
      ;;
    partial_batch)
      run_agent reserve-batch || { run_agent reservations | grep -q SKU-A || run_agent reserve-batch; }
      ;;
    duplicate_delivery)
      run_agent provision nina@example.test pro --ref provision-nina || { run_agent accounts | grep -q nina || run_agent provision nina@example.test pro --ref provision-nina; }
      run_agent provision omar@example.test starter --ref provision-omar
      ;;
