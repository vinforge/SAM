#!/usr/bin/env python3
"""
SAM Introspection Dashboard - API Endpoints
===========================================

This module provides REST API endpoints for the SAM Introspection Dashboard,
enabling real-time access to trace data, performance metrics, and debugging
information.

Endpoints:
- GET /api/trace/<trace_id> - Get complete trace events
- GET /api/trace/<trace_id>/summary - Get trace summary
- GET /api/trace/<trace_id>/timeline - Get timeline-formatted events
- POST /api/trace/query - Initiate a new traced query
- GET /api/trace/active - List active traces
- DELETE /api/trace/<trace_id> - Clean up trace data

Author: SAM Development Team
Version: 1.0.0
"""

import json
import time
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging

# Import the trace logger
try:
    from sam.cognition.trace_logger import get_trace_logger, EventType, Severity
except ImportError:
    # Fallback for development
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from sam.cognition.trace_logger import get_trace_logger, EventType, Severity

# Configure logging
logger = logging.getLogger(__name__)

# Create Flask app for trace API
trace_app = Flask(__name__)
CORS(trace_app)  # Enable CORS for frontend access

@trace_app.route('/api/trace/<trace_id>', methods=['GET'])
def get_trace_events(trace_id: str):
    """
    Get complete trace events for a specific trace ID.
    
    Args:
        trace_id: Unique trace identifier
        
    Returns:
        JSON response with trace events
    """
    try:
        trace_logger = get_trace_logger()
        events = trace_logger.get_trace_events(trace_id)
        
        if not events:
            return jsonify({
                'success': False,
                'error': 'Trace not found',
                'trace_id': trace_id
            }), 404
        
        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'events': events,
            'event_count': len(events),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving trace {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/<trace_id>/summary', methods=['GET'])
def get_trace_summary(trace_id: str):
    """
    Get high-level summary for a specific trace.
    
    Args:
        trace_id: Unique trace identifier
        
    Returns:
        JSON response with trace summary
    """
    try:
        trace_logger = get_trace_logger()
        summary = trace_logger.get_trace_summary(trace_id)
        
        if not summary:
            return jsonify({
                'success': False,
                'error': 'Trace not found',
                'trace_id': trace_id
            }), 404
        
        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'summary': summary,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving trace summary {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/<trace_id>/timeline', methods=['GET'])
def get_trace_timeline(trace_id: str):
    """
    Get events formatted for timeline visualization.
    
    Args:
        trace_id: Unique trace identifier
        
    Returns:
        JSON response with timeline-formatted events
    """
    try:
        trace_logger = get_trace_logger()
        events = trace_logger.get_trace_events(trace_id)
        
        if not events:
            return jsonify({
                'success': False,
                'error': 'Trace not found',
                'trace_id': trace_id
            }), 404
        
        # Format events for timeline visualization
        timeline_events = []
        for event in events:
            timeline_event = {
                'id': event['event_id'],
                'timestamp': event['timestamp'],
                'module': event['source_module'],
                'type': event['event_type'],
                'severity': event['severity'],
                'message': event['message'],
                'duration': event.get('duration_ms'),
                'parent': event.get('parent_event_id'),
                'expandable': bool(event.get('payload') or event.get('metadata'))
            }
            timeline_events.append(timeline_event)
        
        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'timeline': timeline_events,
            'event_count': len(timeline_events),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving trace timeline {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/query', methods=['POST'])
def initiate_traced_query():
    """
    Initiate a new traced query.
    
    Request Body:
        {
            "query": "User query text",
            "user_id": "optional_user_id",
            "session_id": "optional_session_id",
            "trace_mode": "manual|auto|session|performance"
        }
        
    Returns:
        JSON response with trace_id for monitoring
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        query = data['query']
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        trace_mode = data.get('trace_mode', 'manual')
        
        # Start the trace
        trace_logger = get_trace_logger()
        trace_id = trace_logger.start_trace(
            query=query,
            user_id=user_id,
            session_id=session_id
        )
        
        # Log the trace initiation
        trace_logger.log_event(
            trace_id=trace_id,
            source_module="TraceAPI",
            event_type=EventType.START,
            severity=Severity.INFO,
            message=f"Trace initiated via API with mode: {trace_mode}",
            payload={
                'trace_mode': trace_mode,
                'api_endpoint': '/api/trace/query',
                'request_timestamp': time.time()
            }
        )
        
        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'query': query,
            'trace_mode': trace_mode,
            'timestamp': time.time(),
            'polling_url': f'/api/trace/{trace_id}',
            'timeline_url': f'/api/trace/{trace_id}/timeline'
        })
        
    except Exception as e:
        logger.error(f"Error initiating traced query: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/active', methods=['GET'])
def get_active_traces():
    """
    Get list of currently active traces.
    
    Returns:
        JSON response with active trace IDs and summaries
    """
    try:
        trace_logger = get_trace_logger()
        active_trace_ids = trace_logger.get_active_traces()
        
        # Get summaries for active traces
        active_traces = []
        for trace_id in active_trace_ids:
            summary = trace_logger.get_trace_summary(trace_id)
            if summary:
                active_traces.append(summary)
        
        return jsonify({
            'success': True,
            'active_traces': active_traces,
            'count': len(active_traces),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving active traces: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/<trace_id>', methods=['DELETE'])
def cleanup_trace(trace_id: str):
    """
    Clean up trace data for a specific trace.
    
    Args:
        trace_id: Unique trace identifier
        
    Returns:
        JSON response confirming cleanup
    """
    try:
        trace_logger = get_trace_logger()
        
        # Check if trace exists
        summary = trace_logger.get_trace_summary(trace_id)
        if not summary:
            return jsonify({
                'success': False,
                'error': 'Trace not found',
                'trace_id': trace_id
            }), 404
        
        # For now, we'll just mark it as cleaned up
        # In a full implementation, we'd remove it from storage
        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'message': 'Trace cleanup requested',
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up trace {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/<trace_id>/performance', methods=['GET'])
def get_trace_performance(trace_id: str):
    """
    Get detailed performance metrics for a trace.
    
    Args:
        trace_id: Unique trace identifier
        
    Returns:
        JSON response with performance metrics
    """
    try:
        trace_logger = get_trace_logger()
        events = trace_logger.get_trace_events(trace_id)
        
        if not events:
            return jsonify({
                'success': False,
                'error': 'Trace not found',
                'trace_id': trace_id
            }), 404
        
        # Calculate performance metrics
        performance_metrics = {
            'total_events': len(events),
            'modules_involved': len(set(event['source_module'] for event in events)),
            'event_types': {},
            'severity_distribution': {},
            'duration_stats': {},
            'timeline_analysis': {}
        }
        
        # Analyze event types and severities
        for event in events:
            event_type = event['event_type']
            severity = event['severity']
            
            performance_metrics['event_types'][event_type] = \
                performance_metrics['event_types'].get(event_type, 0) + 1
            performance_metrics['severity_distribution'][severity] = \
                performance_metrics['severity_distribution'].get(severity, 0) + 1
        
        # Calculate duration statistics
        durations = [event.get('duration_ms', 0) for event in events if event.get('duration_ms')]
        if durations:
            performance_metrics['duration_stats'] = {
                'total_duration_ms': sum(durations),
                'average_duration_ms': sum(durations) / len(durations),
                'max_duration_ms': max(durations),
                'min_duration_ms': min(durations)
            }
        
        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'performance': performance_metrics,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving trace performance {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/analytics', methods=['GET'])
def get_trace_analytics():
    """
    Get aggregated analytics across all traces.

    Query Parameters:
        days: Number of days to analyze (default: 7)
        type: Analytics type (trends|patterns|efficiency|anomalies)

    Returns:
        JSON response with comprehensive analytics
    """
    try:
        from sam.cognition.trace_analytics import get_trace_analytics

        days = int(request.args.get('days', 7))
        analytics_type = request.args.get('type', 'trends')

        analytics_engine = get_trace_analytics()

        if analytics_type == 'trends':
            result = analytics_engine.get_performance_trends(days)
        elif analytics_type == 'patterns':
            limit = int(request.args.get('limit', 100))
            result = analytics_engine.get_query_patterns(limit)
        elif analytics_type == 'efficiency':
            result = analytics_engine.get_module_efficiency(days)
        elif analytics_type == 'anomalies':
            result = analytics_engine.detect_anomalies(days)
        else:
            # Default comprehensive analytics
            result = {
                'performance_trends': analytics_engine.get_performance_trends(days),
                'query_patterns': analytics_engine.get_query_patterns(100),
                'module_efficiency': analytics_engine.get_module_efficiency(days),
                'anomalies': analytics_engine.detect_anomalies(days)
            }

        return jsonify({
            'success': True,
            'analytics': result,
            'analytics_type': analytics_type,
            'period_days': days,
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error retrieving trace analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/history', methods=['GET'])
def get_trace_history():
    """
    Get historical traces with filtering and pagination.

    Query Parameters:
        limit: Number of traces to return (default: 50)
        offset: Pagination offset (default: 0)
        start_date: Filter by start date (timestamp)
        end_date: Filter by end date (timestamp)
        user_id: Filter by user ID
        status: Filter by status (active|completed|failed)
        success: Filter by success (true|false)
        query_contains: Filter by query content

    Returns:
        JSON response with historical traces
    """
    try:
        from sam.cognition.trace_database import get_trace_database

        # Parse query parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        filters = {}
        if request.args.get('start_date'):
            filters['start_date'] = float(request.args.get('start_date'))
        if request.args.get('end_date'):
            filters['end_date'] = float(request.args.get('end_date'))
        if request.args.get('user_id'):
            filters['user_id'] = request.args.get('user_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('success'):
            filters['success'] = request.args.get('success').lower() == 'true'
        if request.args.get('query_contains'):
            filters['query_contains'] = request.args.get('query_contains')

        db = get_trace_database()
        traces = db.get_trace_history(limit=limit, offset=offset, filters=filters)

        return jsonify({
            'success': True,
            'traces': traces,
            'count': len(traces),
            'limit': limit,
            'offset': offset,
            'filters': filters,
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error retrieving trace history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/compare', methods=['POST'])
def compare_traces():
    """
    Compare multiple traces for analysis.

    Request Body:
        {
            "trace_ids": ["trace1", "trace2", ...]
        }

    Returns:
        JSON response with trace comparison
    """
    try:
        from sam.cognition.trace_analytics import get_trace_analytics

        data = request.get_json()
        if not data or 'trace_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'trace_ids array is required'
            }), 400

        trace_ids = data['trace_ids']
        if len(trace_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 trace IDs required for comparison'
            }), 400

        analytics_engine = get_trace_analytics()
        comparison = analytics_engine.compare_traces(trace_ids)

        return jsonify({
            'success': True,
            'comparison': comparison,
            'trace_count': len(trace_ids),
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error comparing traces: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/export', methods=['POST'])
def export_traces():
    """
    Export trace data for external analysis.

    Request Body:
        {
            "trace_ids": ["trace1", "trace2", ...],
            "format": "json|csv",
            "include_events": true|false
        }

    Returns:
        Exported trace data
    """
    try:
        from sam.cognition.trace_database import get_trace_database

        data = request.get_json()
        if not data or 'trace_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'trace_ids array is required'
            }), 400

        trace_ids = data['trace_ids']
        export_format = data.get('format', 'json')
        include_events = data.get('include_events', True)

        db = get_trace_database()
        export_data = {
            'traces': [],
            'export_metadata': {
                'format': export_format,
                'include_events': include_events,
                'exported_at': time.time(),
                'trace_count': len(trace_ids)
            }
        }

        for trace_id in trace_ids:
            # Get trace from database
            traces = db.get_trace_history(limit=1, filters={'trace_id': trace_id})
            if traces:
                trace_data = traces[0]

                if include_events:
                    events = db.get_trace_events_from_db(trace_id)
                    trace_data['events'] = events

                export_data['traces'].append(trace_data)

        if export_format == 'csv':
            # TODO: Implement CSV export
            return jsonify({
                'success': False,
                'error': 'CSV export not yet implemented'
            }), 501

        return jsonify({
            'success': True,
            'export_data': export_data,
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error exporting traces: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/database/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics and health information."""
    try:
        from sam.cognition.trace_database import get_trace_database

        db = get_trace_database()
        stats = db.get_database_stats()

        return jsonify({
            'success': True,
            'database_stats': stats,
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error retrieving database stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@trace_app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# Phase 2A: Advanced Visualization Endpoints

@trace_app.route('/api/trace/<trace_id>/flow', methods=['GET'])
def get_trace_flow_diagram(trace_id: str):
    """Get trace data formatted for flow diagram visualization."""
    try:
        from sam.cognition.trace_analytics import get_trace_analytics
        analytics = get_trace_analytics()

        flow_data = analytics.generate_flow_diagram(trace_id)

        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'flow_diagram': flow_data,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error generating flow diagram for {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/<trace_id>/hierarchy', methods=['GET'])
def get_trace_hierarchy(trace_id: str):
    """Get trace events in hierarchical format with parent-child relationships."""
    try:
        from sam.cognition.trace_analytics import get_trace_analytics
        analytics = get_trace_analytics()

        hierarchy_data = analytics.generate_hierarchy_view(trace_id)

        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'hierarchy': hierarchy_data,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error generating hierarchy view for {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

@trace_app.route('/api/trace/performance/baseline', methods=['GET'])
def get_performance_baseline():
    """Get performance baseline metrics for comparison."""
    try:
        from sam.cognition.trace_analytics import get_trace_analytics
        analytics = get_trace_analytics()

        days = int(request.args.get('days', 7))
        baseline_data = analytics.get_performance_baseline(days)

        return jsonify({
            'success': True,
            'baseline': baseline_data,
            'period_days': days,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting performance baseline: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/trace/<trace_id>/replay', methods=['POST'])
def replay_trace(trace_id: str):
    """Replay a trace with the same parameters for debugging."""
    try:
        from sam.cognition.trace_analytics import get_trace_analytics
        analytics = get_trace_analytics()

        replay_options = request.get_json() or {}
        replay_result = analytics.replay_trace(trace_id, replay_options)

        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'replay_result': replay_result,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error replaying trace {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace_id': trace_id
        }), 500

# Phase 2B: Production Features Endpoints

@trace_app.route('/api/admin/security/status', methods=['GET'])
def get_security_status():
    """Get security system status."""
    try:
        from sam.cognition.trace_security import get_security_manager
        security_manager = get_security_manager()

        # Get security statistics
        stats = {
            'active_sessions': len(security_manager.sessions),
            'total_users': len(security_manager.users),
            'recent_alerts': len([
                alert for alert in security_manager.audit_log[-10:]
                if alert.event_type.value in ['unauthorized_access', 'security_violation']
            ]),
            'failed_attempts_today': len([
                alert for alert in security_manager.audit_log
                if alert.event_type.value == 'login_failure' and
                alert.timestamp.date() == datetime.now().date()
            ])
        }

        return jsonify({
            'success': True,
            'security_status': stats,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/retention/stats', methods=['GET'])
def get_retention_stats():
    """Get data retention statistics."""
    try:
        from sam.cognition.trace_retention import get_retention_manager
        retention_manager = get_retention_manager()

        stats = retention_manager.get_retention_stats()

        return jsonify({
            'success': True,
            'retention_stats': stats,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting retention stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/retention/cleanup/<job_id>', methods=['POST'])
def run_cleanup_job(job_id: str):
    """Run a specific cleanup job."""
    try:
        from sam.cognition.trace_retention import get_retention_manager
        retention_manager = get_retention_manager()

        result = retention_manager.run_cleanup_job(job_id)

        return jsonify({
            'success': True,
            'cleanup_result': {
                'job_id': result.job_id,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat(),
                'records_processed': result.records_processed,
                'records_deleted': result.records_deleted,
                'records_archived': result.records_archived,
                'bytes_freed': result.bytes_freed,
                'success': result.success,
                'errors': result.errors
            },
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error running cleanup job {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/performance/health', methods=['GET'])
def get_system_health():
    """Get comprehensive system health status."""
    try:
        from sam.cognition.trace_performance import get_performance_manager
        performance_manager = get_performance_manager()

        health_data = performance_manager.get_system_health()

        return jsonify({
            'success': True,
            'system_health': health_data,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/alerts/active', methods=['GET'])
def get_active_alerts():
    """Get active alerts."""
    try:
        from sam.cognition.trace_alerting import get_alert_manager
        alert_manager = get_alert_manager()

        active_alerts = alert_manager.get_active_alerts()

        alerts_data = []
        for alert in active_alerts:
            alerts_data.append({
                'alert_id': alert.alert_id,
                'rule_id': alert.rule_id,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'acknowledged': alert.acknowledged,
                'resolved': alert.resolved,
                'channels_sent': [ch.value for ch in alert.channels_sent]
            })

        return jsonify({
            'success': True,
            'active_alerts': alerts_data,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    try:
        from sam.cognition.trace_alerting import get_alert_manager
        alert_manager = get_alert_manager()

        data = request.get_json() or {}
        user = data.get('user', 'api')

        success = alert_manager.acknowledge_alert(alert_id, user)

        return jsonify({
            'success': success,
            'alert_id': alert_id,
            'acknowledged_by': user,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/alerts/statistics', methods=['GET'])
def get_alert_statistics():
    """Get alert statistics."""
    try:
        from sam.cognition.trace_alerting import get_alert_manager
        alert_manager = get_alert_manager()

        stats = alert_manager.get_alert_statistics()

        return jsonify({
            'success': True,
            'alert_statistics': stats,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/admin/goal-engine/stats', methods=['GET'])
def get_goal_engine_stats():
    """Get Goal & Motivation Engine statistics."""
    try:
        from sam.autonomy.motivation_engine import get_motivation_engine
        motivation_engine = get_motivation_engine()

        stats = motivation_engine.get_statistics()

        return jsonify({
            'success': True,
            'goal_engine_stats': stats,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting goal engine stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Phase 3: Interactive Intervention & Live Tuning Endpoints

@trace_app.route('/api/intervention/breakpoints', methods=['GET'])
def get_breakpoints():
    """Get all breakpoints."""
    try:
        from sam.cognition.trace_breakpoints import get_breakpoint_manager
        breakpoint_manager = get_breakpoint_manager()

        breakpoints = breakpoint_manager.get_breakpoints()

        return jsonify({
            'success': True,
            'breakpoints': breakpoints,
            'total_count': len(breakpoints),
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting breakpoints: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/intervention/breakpoints', methods=['POST'])
def create_breakpoint():
    """Create a new breakpoint."""
    try:
        from sam.cognition.trace_breakpoints import get_breakpoint_manager
        from sam.cognition.trace_security import get_security_manager

        # Check authentication and permissions
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        security_manager = get_security_manager()
        if not security_manager.check_permission(session_id, 'intervention', 'create'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        # Validate required fields
        required_fields = ['name', 'description', 'module_name', 'event_type', 'condition']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        breakpoint_manager = get_breakpoint_manager()

        # Get user from session
        session = security_manager.validate_session(session_id)
        created_by = session.username if session else 'unknown'

        breakpoint_id = breakpoint_manager.create_breakpoint(
            name=data['name'],
            description=data['description'],
            module_name=data['module_name'],
            event_type=data['event_type'],
            condition=data['condition'],
            created_by=created_by,
            max_hits=data.get('max_hits'),
            expires_in_hours=data.get('expires_in_hours')
        )

        return jsonify({
            'success': True,
            'breakpoint_id': breakpoint_id,
            'message': f'Breakpoint "{data["name"]}" created successfully',
            'timestamp': time.time()
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating breakpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/intervention/breakpoints/<breakpoint_id>', methods=['DELETE'])
def delete_breakpoint(breakpoint_id: str):
    """Delete a breakpoint."""
    try:
        from sam.cognition.trace_breakpoints import get_breakpoint_manager
        from sam.cognition.trace_security import get_security_manager

        # Check authentication and permissions
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        security_manager = get_security_manager()
        if not security_manager.check_permission(session_id, 'intervention', 'delete'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        breakpoint_manager = get_breakpoint_manager()

        if breakpoint_id not in breakpoint_manager.breakpoints:
            return jsonify({'success': False, 'error': 'Breakpoint not found'}), 404

        del breakpoint_manager.breakpoints[breakpoint_id]
        breakpoint_manager._save_breakpoints()

        return jsonify({
            'success': True,
            'message': f'Breakpoint {breakpoint_id} deleted successfully',
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error deleting breakpoint {breakpoint_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/intervention/paused-traces', methods=['GET'])
def get_paused_traces():
    """Get all paused traces."""
    try:
        from sam.cognition.trace_breakpoints import get_breakpoint_manager
        breakpoint_manager = get_breakpoint_manager()

        paused_traces = breakpoint_manager.get_paused_traces()

        return jsonify({
            'success': True,
            'paused_traces': paused_traces,
            'total_count': len(paused_traces),
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting paused traces: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/intervention/traces/<trace_id>/resume', methods=['POST'])
def resume_trace(trace_id: str):
    """Resume a paused trace."""
    try:
        from sam.cognition.trace_breakpoints import get_breakpoint_manager
        from sam.cognition.trace_security import get_security_manager

        # Check authentication and permissions
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        security_manager = get_security_manager()
        if not security_manager.check_permission(session_id, 'intervention', 'resume'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        data = request.get_json() or {}
        override_payload = data.get('override_payload')

        breakpoint_manager = get_breakpoint_manager()

        # Get user from session
        session = security_manager.validate_session(session_id)
        resolved_by = session.username if session else 'unknown'

        success = breakpoint_manager.resume_trace(trace_id, resolved_by, override_payload)

        if not success:
            return jsonify({'success': False, 'error': 'Trace not found or not paused'}), 404

        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'message': f'Trace resumed by {resolved_by}',
            'override_applied': override_payload is not None,
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error resuming trace {trace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/intervention/breakpoints/<breakpoint_id>/toggle', methods=['POST'])
def toggle_breakpoint(breakpoint_id: str):
    """Enable or disable a breakpoint."""
    try:
        from sam.cognition.trace_breakpoints import get_breakpoint_manager
        from sam.cognition.trace_security import get_security_manager

        # Check authentication and permissions
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        security_manager = get_security_manager()
        if not security_manager.check_permission(session_id, 'intervention', 'modify'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        breakpoint_manager = get_breakpoint_manager()

        if breakpoint_id not in breakpoint_manager.breakpoints:
            return jsonify({'success': False, 'error': 'Breakpoint not found'}), 404

        breakpoint = breakpoint_manager.breakpoints[breakpoint_id]
        breakpoint.enabled = not breakpoint.enabled
        breakpoint_manager._save_breakpoints()

        return jsonify({
            'success': True,
            'breakpoint_id': breakpoint_id,
            'enabled': breakpoint.enabled,
            'message': f'Breakpoint {"enabled" if breakpoint.enabled else "disabled"}',
            'timestamp': time.time()
        })

    except Exception as e:
        logger.error(f"Error toggling breakpoint {breakpoint_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Live Rule System Endpoints

@trace_app.route('/api/live-rules', methods=['GET'])
def get_live_rules():
    """Get all live rules."""
    try:
        from sam.cognition.live_rules import get_live_rule_manager
        rule_manager = get_live_rule_manager()

        rules = rule_manager.get_rules()

        return jsonify({
            'success': True,
            'rules': rules,
            'total_count': len(rules),
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Error getting live rules: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trace_app.route('/api/live-rules', methods=['POST'])
def create_live_rule():
    """Create a new live rule."""
    try:
        from sam.cognition.live_rules import get_live_rule_manager, RuleType
        from sam.cognition.trace_security import get_security_manager

        # Check authentication and permissions
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        security_manager = get_security_manager()
        if not security_manager.check_permission(session_id, 'live_rules', 'create'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        # Validate required fields
        required_fields = ['name', 'description', 'rule_type', 'target_module', 'target_function', 'condition', 'action']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        rule_manager = get_live_rule_manager()

        # Get user from session
        session = security_manager.validate_session(session_id)
        created_by = session.username if session else 'unknown'

        rule_id = rule_manager.create_rule(
            name=data['name'],
            description=data['description'],
            rule_type=RuleType(data['rule_type']),
            target_module=data['target_module'],
            target_function=data['target_function'],
            condition=data['condition'],
            action=data['action'],
            created_by=created_by,
            priority=data.get('priority', 100),
            max_applications=data.get('max_applications'),
            expires_in_hours=data.get('expires_in_hours'),
            test_mode=data.get('test_mode', False)
        )

        return jsonify({
            'success': True,
            'rule_id': rule_id,
            'message': f'Live rule "{data["name"]}" created successfully',
            'timestamp': time.time()
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating live rule: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def create_trace_api_app() -> Flask:
    """Create and configure the trace API Flask app."""
    return trace_app

if __name__ == '__main__':
    # For development testing
    trace_app.run(debug=True, port=5002)
