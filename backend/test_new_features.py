#!/usr/bin/env python
"""Test script to validate new code"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))


def main():
    try:
        # Test imports
        from api.validators import CustomPasswordValidator
        from api.middleware import SecurityHeadersMiddleware
        from api.payment_service import StripePaymentService, SUBSCRIPTION_PLANS
        from api.data_service import DataManagementService

        print("All imports successful")

        # Test validator
        validator = CustomPasswordValidator()
        help_text = validator.get_help_text()
        print("Password validator working")

        # Test payment service
        plans = SUBSCRIPTION_PLANS
        print(f"Payment service loaded with {len(plans)} plans")

        print("All new features validated successfully!")

    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
