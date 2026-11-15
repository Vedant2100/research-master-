    commit_timeout)
      run_agent pay INV-104 12500 --ref payout-INV-104 || run_agent pay INV-104 12500 --ref payout-INV-104
      run_agent pay INV-105 8300 --ref payout-INV-105
      ;;
    stale_read)
      run_agent grant maya billing_admin --ref grant-maya-billing
      if ! run_agent members | grep -q '"role": "billing_admin", "user": "maya"\|"user": "maya", "role": "billing_admin"'; then
        run_agent grant maya billing_admin --ref grant-maya-billing
      fi
      ;;
    partial_batch)
      run_agent reserve-batch || run_agent reserve-batch
      ;;
    duplicate_delivery)
      run_agent provision nina@example.test pro --ref provision-nina || run_agent provision nina@example.test pro --ref provision-nina
      run_agent provision omar@example.test starter --ref provision-omar
      ;;
