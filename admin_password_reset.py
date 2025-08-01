#!/usr/bin/env python3
"""
Secure Admin Password Reset Script
Use this to change the menchayheng admin password to whatever you want
"""

import sys
import getpass
import sqlite3
sys.path.append('.')
from login import hash_password

def reset_admin_password():
    """Reset the menchayheng admin password"""
    print("🔐 Admin Password Reset Tool")
    print("=" * 50)
    print("This will reset the password for user: menchayheng")
    print()
    
    # Confirm the action
    confirm = input("Are you sure you want to reset the admin password? (yes/no): ").lower()
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        return
    
    # Get new password
    while True:
        print("\nEnter new admin password:")
        new_password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if new_password != confirm_password:
            print("❌ Passwords don't match. Please try again.")
            continue
        
        if len(new_password) < 6:
            print("❌ Password must be at least 6 characters long.")
            continue
        
        break
    
    try:
        # Hash the password
        hashed_password = hash_password(new_password)
        
        # Update the database
        conn = sqlite3.connect('data/user_database.db')
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute('SELECT id, username FROM users WHERE username = ?', ('menchayheng',))
        user = cursor.fetchone()
        
        if not user:
            print("❌ Admin user 'menchayheng' not found in database!")
            conn.close()
            return
        
        user_id, username = user
        print(f"✅ Found admin user: {username} (ID: {user_id})")
        
        # Reset password and clear any locks/failed attempts
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, failed_attempts = 0, locked_until = NULL 
            WHERE username = ?
        ''', (hashed_password, 'menchayheng'))
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Admin password reset successfully!")
            print(f"Username: menchayheng")
            print("Password: [hidden for security]")
            print()
            print("🔒 Security Notes:")
            print("- The password is now changed")
            print("- All failed login attempts have been cleared")
            print("- Any account locks have been removed")
            print("- You can now log in with the new password")
        else:
            print("❌ Failed to update password")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")

if __name__ == "__main__":
    reset_admin_password()