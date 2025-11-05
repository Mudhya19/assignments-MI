"""
API Module for BPJS Database Operations
This module provides access to database functionality for BPJS monitoring.
"""

from .database import DatabaseManager, BPJSQueryManager

# Expose the main classes for easy import
__all__ = ['DatabaseManager', 'BPJSQueryManager']

# Convenience functions for common operations
def get_database_manager():
    """Create and return a DatabaseManager instance"""
    return DatabaseManager()

def get_bpjs_query_manager():
    """Create and return a BPJSQueryManager instance"""
    return BPJSQueryManager()

# Example usage:
# from database.api import get_bpjs_query_manager
# manager = get_bpjs_query_manager()
# data = manager.load_patient_data('2023-01-01', '2023-12-31')