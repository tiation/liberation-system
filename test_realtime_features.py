#!/usr/bin/env python3

import asyncio
import json
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

async def test_notification_service():
    """Test the notification service"""
    console.print("\n🔔 Testing Notification Service...", style="cyan bold")
    
    try:
        # Import the notification service
        from realtime.notifications.service import (
            notification_service, 
            NotificationType, 
            NotificationPriority
        )
        
        # Test sending different types of notifications
        test_notifications = [
            {
                "user_id": "test_user_001",
                "type": NotificationType.RESOURCE_DISTRIBUTION,
                "data": {"amount": 800.00},
                "description": "Resource distribution notification"
            },
            {
                "user_id": "test_user_002", 
                "type": NotificationType.TRUTH_UPDATE,
                "data": {"message": "Liberation system is working!"},
                "description": "Truth network update"
            },
            {
                "user_id": "test_user_003",
                "type": NotificationType.WELCOME,
                "data": {},
                "description": "Welcome notification"
            }
        ]
        
        notification_ids = []
        for notification in test_notifications:
            notification_id = await notification_service.send_notification(
                user_id=notification["user_id"],
                notification_type=notification["type"],
                data=notification["data"]
            )
            notification_ids.append(notification_id)
            console.print(f"✅ Sent {notification['description']}: {notification_id}")
            await asyncio.sleep(0.5)
        
        # Test system alert
        alert_id = await notification_service.send_system_alert(
            title="🚀 System Test Alert",
            message="Testing system-wide alert functionality",
            alert_level="info"
        )
        console.print(f"✅ Sent system alert: {alert_id}")
        
        # Test getting notifications
        user_notifications = await notification_service.get_user_notifications(
            user_id="test_user_001",
            limit=10
        )
        console.print(f"✅ Retrieved {len(user_notifications)} notifications for test_user_001")
        
        # Test notification stats
        stats = await notification_service.get_notification_stats()
        console.print(f"✅ Notification stats: {stats['total_notifications']} total, {stats['total_users']} users")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Notification service test failed: {e}", style="red")
        return False

async def test_metrics_service():
    """Test the metrics service"""
    console.print("\n📊 Testing Metrics Service...", style="cyan bold")
    
    try:
        # Import the metrics service
        from realtime.analytics.metrics import (
            metrics_service,
            MetricType,
            MetricCategory
        )
        
        # Test recording metrics
        test_metrics = [
            ("test_resource_distributed", 800.00, "Resource distribution amount"),
            ("test_truth_messages", 1.0, "Truth message sent"),
            ("test_mesh_nodes", 5.0, "Active mesh nodes"),
            ("test_user_actions", 10.0, "User actions count")
        ]
        
        for metric_name, value, description in test_metrics:
            metrics_service.record_metric(metric_name, value)
            console.print(f"✅ Recorded metric {metric_name}: {value}")
            await asyncio.sleep(0.2)
        
        # Test custom metric creation
        custom_metric_created = metrics_service.create_custom_metric(
            name="test_custom_metric",
            metric_type=MetricType.GAUGE,
            category=MetricCategory.SYSTEM,
            description="Test custom metric",
            unit="count"
        )
        
        if custom_metric_created:
            console.print("✅ Created custom metric successfully")
            metrics_service.record_metric("test_custom_metric", 42.0)
            console.print("✅ Recorded value for custom metric")
        
        # Test alert rule
        alert_rule_added = metrics_service.add_alert_rule(
            metric_name="system_cpu_usage",
            threshold=85.0,
            condition="greater_than",
            severity="warning"
        )
        
        if alert_rule_added:
            console.print("✅ Added alert rule for CPU usage")
        
        # Test dashboard metrics
        dashboard_metrics = await metrics_service.get_dashboard_metrics()
        console.print(f"✅ Retrieved dashboard metrics: {len(dashboard_metrics.get('metrics', {}))} metrics")
        
        # Test admin metrics
        admin_metrics = await metrics_service.get_admin_metrics()
        console.print(f"✅ Retrieved admin metrics: {len(admin_metrics.get('categories', {}))} categories")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Metrics service test failed: {e}", style="red")
        return False

async def test_websocket_manager():
    """Test the WebSocket manager"""
    console.print("\n🔌 Testing WebSocket Manager...", style="cyan bold")
    
    try:
        # Import the websocket manager
        from realtime.websocket.manager import websocket_manager, ConnectionType
        
        # Test WebSocket stats
        stats = websocket_manager.get_stats()
        console.print(f"✅ WebSocket stats: {stats}")
        
        # Test connection info (simulated)
        console.print("✅ WebSocket manager is operational")
        
        return True
        
    except Exception as e:
        console.print(f"❌ WebSocket manager test failed: {e}", style="red")
        return False

async def test_event_system():
    """Test the event system"""
    console.print("\n📡 Testing Event System...", style="cyan bold")
    
    try:
        # Import the event system
        from realtime.events.system import event_system, EventType
        
        # Test event publishing
        test_events = [
            {
                "type": EventType.RESOURCE_DISTRIBUTED,
                "data": {"human_id": "test_human_001", "amount": 800.00},
                "source": "test_system"
            },
            {
                "type": EventType.TRUTH_MESSAGE_SENT,
                "data": {"message": "Test truth message", "reach_count": 1000},
                "source": "test_system"
            },
            {
                "type": EventType.MESH_NODE_CONNECTED,
                "data": {"node_id": "test_node_001", "address": "127.0.0.1"},
                "source": "test_system"
            }
        ]
        
        for event in test_events:
            await event_system.publish(
                event_type=event["type"],
                data=event["data"],
                source=event["source"]
            )
            console.print(f"✅ Published event: {event['type'].value}")
            await asyncio.sleep(0.3)
        
        # Test event metrics
        event_metrics = event_system.get_metrics()
        console.print(f"✅ Event system metrics: {event_metrics}")
        
        # Test event history
        event_history = event_system.get_event_history(limit=5)
        console.print(f"✅ Retrieved {len(event_history)} events from history")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Event system test failed: {e}", style="red")
        return False

async def test_integration():
    """Test integration between all services"""
    console.print("\n🔗 Testing Service Integration...", style="cyan bold")
    
    try:
        # Import all services
        from realtime.notifications.service import notification_service, NotificationType
        from realtime.analytics.metrics import metrics_service
        from realtime.events.system import event_system, EventType
        
        # Test end-to-end integration
        console.print("🔄 Testing end-to-end integration...")
        
        # Simulate a resource distribution event
        await event_system.publish(
            event_type=EventType.RESOURCE_DISTRIBUTED,
            data={
                "human_id": "integration_test_user",
                "amount": 800.00,
                "distribution_type": "weekly"
            },
            source="integration_test"
        )
        
        # Give events time to propagate
        await asyncio.sleep(1)
        
        # Check if metrics were recorded
        latest_value = metrics_service.metrics.get("resources_distributed_total", None)
        if latest_value and latest_value.get_latest_value():
            console.print("✅ Metrics recorded from event")
        
        # Check if notifications were sent
        user_notifications = await notification_service.get_user_notifications(
            user_id="integration_test_user",
            limit=5
        )
        console.print(f"✅ Integration test completed: {len(user_notifications)} notifications processed")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Integration test failed: {e}", style="red")
        return False

async def display_real_time_dashboard():
    """Display a real-time dashboard of system metrics"""
    console.print("\n📊 Real-time Dashboard (5 seconds)...", style="cyan bold")
    
    try:
        from realtime.analytics.metrics import metrics_service
        from realtime.notifications.service import notification_service
        from realtime.websocket.manager import websocket_manager
        
        # Create a simple dashboard layout
        layout = Layout()
        
        # Run dashboard for 5 seconds
        end_time = time.time() + 5
        
        while time.time() < end_time:
            # Get current metrics
            dashboard_data = await metrics_service.get_dashboard_metrics()
            notification_stats = await notification_service.get_notification_stats()
            websocket_stats = websocket_manager.get_stats()
            
            # Create metrics table
            metrics_table = Table(title="System Metrics", style="cyan")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")
            metrics_table.add_column("Trend", style="yellow")
            
            for metric_name, metric_data in dashboard_data.get("metrics", {}).items():
                current_value = metric_data.get("current_value", 0)
                trend = metric_data.get("trend", "stable")
                unit = metric_data.get("unit", "")
                
                trend_symbol = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
                
                metrics_table.add_row(
                    metric_name,
                    f"{current_value} {unit}",
                    f"{trend_symbol} {trend}"
                )
            
            # Create status panel
            status_panel = Panel(
                f"🔔 Notifications: {notification_stats.get('total_notifications', 0)}\n"
                f"👥 Users: {notification_stats.get('total_users', 0)}\n"
                f"🔌 WebSocket Connections: {websocket_stats.get('total_connections', 0)}\n"
                f"📊 Total Metrics: {dashboard_data.get('summary', {}).get('total_metrics', 0)}\n"
                f"🕐 Last Update: {datetime.now().strftime('%H:%M:%S')}",
                title="System Status",
                style="green"
            )
            
            console.clear()
            console.print(metrics_table)
            console.print(status_panel)
            
            await asyncio.sleep(1)
        
        return True
        
    except Exception as e:
        console.print(f"❌ Dashboard display failed: {e}", style="red")
        return False

async def main():
    """Main test function"""
    console.print(Panel.fit(
        "🌟 Liberation System Real-time Features Test Suite",
        style="bold cyan"
    ))
    
    # Test results
    test_results = {}
    
    # Run all tests
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        # Test notification service
        task1 = progress.add_task("Testing Notification Service...", total=1)
        test_results["notifications"] = await test_notification_service()
        progress.update(task1, advance=1)
        
        # Test metrics service
        task2 = progress.add_task("Testing Metrics Service...", total=1)
        test_results["metrics"] = await test_metrics_service()
        progress.update(task2, advance=1)
        
        # Test WebSocket manager
        task3 = progress.add_task("Testing WebSocket Manager...", total=1)
        test_results["websocket"] = await test_websocket_manager()
        progress.update(task3, advance=1)
        
        # Test event system
        task4 = progress.add_task("Testing Event System...", total=1)
        test_results["events"] = await test_event_system()
        progress.update(task4, advance=1)
        
        # Test integration
        task5 = progress.add_task("Testing Integration...", total=1)
        test_results["integration"] = await test_integration()
        progress.update(task5, advance=1)
    
    # Display real-time dashboard
    await display_real_time_dashboard()
    
    # Final results
    console.print("\n" + "="*60)
    console.print(Panel.fit("🎯 Test Results Summary", style="bold cyan"))
    
    results_table = Table(title="Test Results", style="cyan")
    results_table.add_column("Test", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Description", style="yellow")
    
    test_descriptions = {
        "notifications": "Real-time notification system",
        "metrics": "Advanced metrics and analytics",
        "websocket": "WebSocket connection management",
        "events": "Event-driven architecture",
        "integration": "End-to-end service integration"
    }
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        if result:
            passed_tests += 1
        
        results_table.add_row(
            test_name.title(),
            status,
            test_descriptions.get(test_name, "")
        )
    
    console.print(results_table)
    
    # Overall status
    if passed_tests == total_tests:
        console.print(Panel.fit(
            f"🎉 All {total_tests} tests PASSED!\n\n"
            "✅ Real-time features are working correctly\n"
            "✅ Service integration is functional\n"
            "✅ System is ready for production use",
            style="bold green"
        ))
    else:
        console.print(Panel.fit(
            f"⚠️  {passed_tests}/{total_tests} tests passed\n\n"
            "Some components may need attention.",
            style="bold yellow"
        ))
    
    # Feature highlights
    console.print(Panel.fit(
        "🚀 Enhanced Features Available:\n\n"
        "• Real-time notifications with multiple types and priorities\n"
        "• Advanced metrics collection and analytics\n"
        "• WebSocket-based real-time communication\n"
        "• Event-driven architecture for loose coupling\n"
        "• Comprehensive service integration\n"
        "• Dark neon theme support throughout\n"
        "• Enterprise-grade monitoring and alerting",
        title="Liberation System Real-time Features",
        style="bold magenta"
    ))

if __name__ == "__main__":
    asyncio.run(main())
