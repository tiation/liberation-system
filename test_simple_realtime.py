#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel

console = Console()

async def test_basic_imports():
    """Test that we can import all the real-time components"""
    try:
        # Test notification service
        from realtime.notifications.service import notification_service, NotificationType
        console.print("✅ Notification service imported successfully")
        
        # Test metrics service
        from realtime.analytics.metrics import metrics_service, MetricType, MetricCategory
        console.print("✅ Metrics service imported successfully")
        
        # Test WebSocket manager
        from realtime.websocket.manager import websocket_manager, ConnectionType
        console.print("✅ WebSocket manager imported successfully")
        
        # Test event system
        from realtime.events.system import event_system, EventType
        console.print("✅ Event system imported successfully")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Import failed: {e}", style="red")
        return False

async def test_basic_functionality():
    """Test basic functionality of each service"""
    try:
        from realtime.notifications.service import notification_service, NotificationType
        from realtime.analytics.metrics import metrics_service
        from realtime.events.system import event_system, EventType
        
        # Test notification service
        notification_id = await notification_service.send_notification(
            user_id="test_user",
            notification_type=NotificationType.RESOURCE_DISTRIBUTION,
            data={"amount": 800.00}
        )
        console.print(f"✅ Notification sent: {notification_id}")
        
        # Test metrics service
        metrics_service.record_metric("test_metric", 42.0)
        console.print("✅ Metric recorded successfully")
        
        # Test event system
        await event_system.publish(
            event_type=EventType.RESOURCE_DISTRIBUTED,
            data={"human_id": "test_human", "amount": 800.00},
            source="test_system"
        )
        console.print("✅ Event published successfully")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Functionality test failed: {e}", style="red")
        return False

async def main():
    """Main test function"""
    console.print(Panel.fit(
        "🚀 Liberation System Real-time Features - Simple Test",
        style="bold cyan"
    ))
    
    # Test imports
    console.print("\n📦 Testing imports...")
    import_success = await test_basic_imports()
    
    if not import_success:
        console.print(Panel.fit(
            "❌ Import test failed. Please check the installation.",
            style="bold red"
        ))
        return
    
    # Test functionality
    console.print("\n🔧 Testing basic functionality...")
    func_success = await test_basic_functionality()
    
    if func_success:
        console.print(Panel.fit(
            "🎉 All tests passed! Real-time features are working correctly.",
            style="bold green"
        ))
    else:
        console.print(Panel.fit(
            "❌ Functionality test failed. Please check the implementation.",
            style="bold red"
        ))

if __name__ == "__main__":
    asyncio.run(main())
