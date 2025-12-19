
import pandas as pd
import sys
import os

# Add current dir to path to import local modules
sys.path.append(os.getcwd())

try:
    from dashboard_propietario import load_data, get_dashboard_context
    print("[INFO] Successfully imported dashboard_propietario")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

try:
    print("[INFO] Testing load_data()...")
    data = load_data()
    if len(data) != 7:
        print(f"[FAIL] Expected 7 return values, got {len(data)}")
        sys.exit(1)
    
    df, sales, recipes, reviews, mermas, rrhh, reservations = data
    print("[PASS] load_data() returned 7 items")
    
    print(f"[INFO] RRHH Shape: {rrhh.shape}")
    print(f"[INFO] Reservations Shape: {reservations.shape}")
    
    # Simple check if rrhh has 'total_pay' and reservations has 'date'
    if 'total_pay' not in rrhh.columns:
         print("[FAIL] 'total_pay' column missing in RRHH")
    
    if 'pax' not in reservations.columns:
         print("[FAIL] 'pax' column missing in Reservations")
         
    print("[INFO] Testing get_dashboard_context signature...")
    # We won't run the full function as it builds a huge string, but we call it to ensure no immediate NameErrors within the top block logic
    # We'll just pass them in and assume if it runs without argument error, the signature is updated.
    
    # To really test runtime errors inside the function (like undefined variables), we should call it.
    # It returns a string.
    try:
        context = get_dashboard_context(df, sales, mermas, reviews, recipes, rrhh, reservations)
        print("[PASS] get_dashboard_context() execution successful")
        print(f"[INFO] Context length: {len(context)}")
    except Exception as e:
        print(f"[FAIL] get_dashboard_context execution failed: {e}")
        sys.exit(1)

except Exception as e:
    print(f"[FAIL] Unexpected error: {e}")
    sys.exit(1)

print("[SUCCESS] All checks passed.")
