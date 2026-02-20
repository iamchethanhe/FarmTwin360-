"""
Script to generate notifications for existing incidents that were created before the notification system was added.
Run this once to create notifications for historical data.
"""

from database import get_db
from models import Incident, Checklist, User, Alert, Barn
from datetime import datetime

def generate_incident_notifications():
    """Generate notifications for existing incidents"""
    db = get_db()
    try:
        # Get all incidents without notifications
        incidents = db.query(Incident).all()
        
        print(f"\nFound {len(incidents)} incidents in database")
        print("=" * 60)
        
        notifications_created = 0
        
        for incident in incidents:
            # Get incident details
            user = db.query(User).filter(User.id == incident.user_id).first()
            barn = db.query(Barn).filter(Barn.id == incident.barn_id).first()
            
            if not user or not barn:
                print(f"⚠️  Skipping incident {incident.id} - missing user or barn")
                continue
            
            # Determine who to notify
            notification_roles = ['admin', 'manager']
            if incident.severity == 'high' or incident.incident_type == 'disease':
                notification_roles.append('vet')
            
            # Get users to notify
            notification_users = db.query(User).filter(
                User.role.in_(notification_roles),
                User.is_active == True
            ).all()
            
            print(f"\nIncident #{incident.id}:")
            print(f"  Reporter: {user.name}")
            print(f"  Barn: {barn.name}")
            print(f"  Type: {incident.incident_type}")
            print(f"  Severity: {incident.severity}")
            print(f"  Approved: {'Yes' if incident.approved else 'No'}")
            print(f"  Notifying {len(notification_users)} users: {notification_roles}")
            
            # Create notifications
            for notif_user in notification_users:
                # Check if notification already exists
                existing = db.query(Alert).filter(
                    Alert.user_id == notif_user.id,
                    Alert.barn_id == barn.id,
                    Alert.type == 'incident_reported'
                ).first()
                
                if existing:
                    print(f"    ↳ {notif_user.name} - already has notification, skipping")
                    continue
                
                alert = Alert(
                    type="incident_reported",
                    message=f"🚨 {incident.severity.upper()} incident reported by {user.name} at {barn.name}: {incident.incident_type} - ⚠️ PENDING APPROVAL",
                    severity=incident.severity,
                    barn_id=barn.id,
                    user_id=notif_user.id,
                    read=False,
                    created_at=incident.reported_at  # Use original incident time
                )
                db.add(alert)
                notifications_created += 1
                print(f"    ✓ Created notification for {notif_user.name}")
        
        db.commit()
        print(f"\n{'=' * 60}")
        print(f"✅ Successfully created {notifications_created} notifications!")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


def generate_checklist_notifications():
    """Generate notifications for existing checklists"""
    db = get_db()
    try:
        # Get all checklists without notifications
        checklists = db.query(Checklist).all()
        
        print(f"\nFound {len(checklists)} checklists in database")
        print("=" * 60)
        
        notifications_created = 0
        
        for checklist in checklists:
            # Get checklist details
            user = db.query(User).filter(User.id == checklist.user_id).first()
            barn = db.query(Barn).filter(Barn.id == checklist.barn_id).first()
            
            if not user or not barn:
                print(f"⚠️  Skipping checklist {checklist.id} - missing user or barn")
                continue
            
            # Get users to notify (admins and managers)
            notification_users = db.query(User).filter(
                User.role.in_(['admin', 'manager']),
                User.is_active == True
            ).all()
            
            print(f"\nChecklist #{checklist.id}:")
            print(f"  Reporter: {user.name}")
            print(f"  Barn: {barn.name}")
            print(f"  Approved: {'Yes' if checklist.approved else 'No'}")
            print(f"  Notifying {len(notification_users)} users: ['admin', 'manager']")
            
            # Create notifications
            for notif_user in notification_users:
                # Check if notification already exists
                existing = db.query(Alert).filter(
                    Alert.user_id == notif_user.id,
                    Alert.barn_id == barn.id,
                    Alert.type == 'checklist_submitted'
                ).first()
                
                if existing:
                    print(f"    ↳ {notif_user.name} - already has notification, skipping")
                    continue
                
                alert = Alert(
                    type="checklist_submitted",
                    message=f"New checklist submitted by {user.name} for {barn.name} - ⏳ PENDING REVIEW",
                    severity="low",
                    barn_id=barn.id,
                    user_id=notif_user.id,
                    read=False,
                    created_at=checklist.submitted_at  # Use original checklist time
                )
                db.add(alert)
                notifications_created += 1
                print(f"    ✓ Created notification for {notif_user.name}")
        
        db.commit()
        print(f"\n{'=' * 60}")
        print(f"✅ Successfully created {notifications_created} notifications!")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  RETROACTIVE NOTIFICATION GENERATOR")
    print("=" * 60)
    print("\nThis script will create notifications for existing incidents")
    print("and checklists that were submitted before the notification")
    print("system was implemented.\n")
    
    # Generate notifications for incidents
    print("\n📋 PROCESSING INCIDENTS...")
    generate_incident_notifications()
    
    # Generate notifications for checklists
    print("\n📋 PROCESSING CHECKLISTS...")
    generate_checklist_notifications()
    
    print("\n✅ Done! Refresh your dashboard to see the notifications.\n")
