# core/knowledge_sharing.py

import asyncio
import json
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import aiofiles
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class KnowledgeType(Enum):
    """Types of knowledge in the system"""
    TECHNICAL = "technical"
    PROCESS = "process"
    SOLUTION = "solution"
    INSIGHT = "insight"
    RESOURCE = "resource"
    COLLABORATION = "collaboration"
    OPTIMIZATION = "optimization"

class KnowledgeStatus(Enum):
    """Status of knowledge entries"""
    DRAFT = "draft"
    ACTIVE = "active"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    ENHANCED = "enhanced"

@dataclass
class KnowledgeEntry:
    """Individual knowledge entry"""
    id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    status: KnowledgeStatus
    author: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    version: int = 1
    parent_id: Optional[str] = None
    confidence_score: float = 0.5
    usage_count: int = 0
    effectiveness_rating: float = 0.0
    related_entries: List[str] = None
    
    def __post_init__(self):
        if self.related_entries is None:
            self.related_entries = []

@dataclass
class LearningSession:
    """Collaborative learning session"""
    id: str
    title: str
    description: str
    participants: List[str]
    knowledge_entries: List[str]
    created_at: datetime
    status: str = "active"
    insights_generated: int = 0
    problems_solved: int = 0

@dataclass
class ProblemContext:
    """Context for autonomous problem-solving"""
    id: str
    problem_description: str
    domain: str
    priority: int
    created_at: datetime
    attempted_solutions: List[str]
    status: str = "analyzing"
    confidence_level: float = 0.0

class KnowledgeShareManager:
    """Core knowledge sharing and collaborative learning system"""
    
    def __init__(self, db_path: str = "data/knowledge_sharing.db"):
        self.db_path = db_path
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.knowledge_base: Dict[str, KnowledgeEntry] = {}
        self.learning_sessions: Dict[str, LearningSession] = {}
        self.problem_contexts: Dict[str, ProblemContext] = {}
        self.mesh_network = None  # Will be injected
        
        # AI-driven learning patterns
        self.learning_patterns = {
            'solution_effectiveness': {},
            'collaboration_success': {},
            'knowledge_usage': {},
            'problem_solving_paths': {}
        }
        
    async def initialize(self):
        """Initialize the knowledge sharing system"""
        try:
            # Create database tables
            await self._create_tables()
            
            # Load existing knowledge
            await self._load_knowledge_base()
            
            # Initialize learning patterns
            await self._initialize_learning_patterns()
            
            # Setup autonomous processes
            await self._setup_autonomous_processes()
            
            self.console.print("[green]✅ Knowledge Sharing System initialized[/green]")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge sharing system: {e}")
            raise

    async def _create_tables(self):
        """Create database tables for knowledge storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Knowledge entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                knowledge_type TEXT NOT NULL,
                status TEXT NOT NULL,
                author TEXT NOT NULL,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                parent_id TEXT,
                confidence_score REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                effectiveness_rating REAL DEFAULT 0.0,
                related_entries TEXT
            )
        ''')
        
        # Learning sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                participants TEXT,
                knowledge_entries TEXT,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                insights_generated INTEGER DEFAULT 0,
                problems_solved INTEGER DEFAULT 0
            )
        ''')
        
        # Problem contexts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problem_contexts (
                id TEXT PRIMARY KEY,
                problem_description TEXT NOT NULL,
                domain TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                attempted_solutions TEXT,
                status TEXT DEFAULT 'analyzing',
                confidence_level REAL DEFAULT 0.0
            )
        ''')
        
        # Learning patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    async def _load_knowledge_base(self):
        """Load existing knowledge from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM knowledge_entries')
        rows = cursor.fetchall()
        
        for row in rows:
            entry = KnowledgeEntry(
                id=row[0],
                title=row[1],
                content=row[2],
                knowledge_type=KnowledgeType(row[3]),
                status=KnowledgeStatus(row[4]),
                author=row[5],
                tags=json.loads(row[6]) if row[6] else [],
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8]),
                version=row[9] or 1,
                parent_id=row[10],
                confidence_score=row[11] or 0.5,
                usage_count=row[12] or 0,
                effectiveness_rating=row[13] or 0.0,
                related_entries=json.loads(row[14]) if row[14] else []
            )
            self.knowledge_base[entry.id] = entry
        
        conn.close()
        self.logger.info(f"Loaded {len(self.knowledge_base)} knowledge entries")

    async def _initialize_learning_patterns(self):
        """Initialize AI learning patterns"""
        # Load existing patterns from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM learning_patterns')
        rows = cursor.fetchall()
        
        for row in rows:
            pattern_type = row[1]
            pattern_data = json.loads(row[2])
            self.learning_patterns[pattern_type] = pattern_data
        
        conn.close()
        
        # Initialize default patterns if none exist
        if not self.learning_patterns['solution_effectiveness']:
            self.learning_patterns['solution_effectiveness'] = {
                'success_rates': {},
                'domain_specific': {},
                'collaboration_factors': {}
            }

    async def _setup_autonomous_processes(self):
        """Setup autonomous learning and optimization processes"""
        # Start background tasks
        asyncio.create_task(self._autonomous_knowledge_optimization())
        asyncio.create_task(self._autonomous_problem_solving())
        asyncio.create_task(self._collaborative_insight_generation())

    async def add_knowledge(self, title: str, content: str, knowledge_type: KnowledgeType, 
                          author: str, tags: List[str] = None) -> str:
        """Add new knowledge to the system"""
        try:
            # Generate unique ID
            entry_id = hashlib.sha256(f"{title}{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # Create knowledge entry
            entry = KnowledgeEntry(
                id=entry_id,
                title=title,
                content=content,
                knowledge_type=knowledge_type,
                status=KnowledgeStatus.DRAFT,
                author=author,
                tags=tags or [],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store in memory
            self.knowledge_base[entry_id] = entry
            
            # Store in database
            await self._save_knowledge_entry(entry)
            
            # Trigger autonomous enhancement
            asyncio.create_task(self._enhance_knowledge_entry(entry_id))
            
            self.logger.info(f"Added knowledge entry: {title}")
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Failed to add knowledge: {e}")
            raise

    async def _save_knowledge_entry(self, entry: KnowledgeEntry):
        """Save knowledge entry to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge_entries 
            (id, title, content, knowledge_type, status, author, tags, created_at, updated_at, 
             version, parent_id, confidence_score, usage_count, effectiveness_rating, related_entries)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.id, entry.title, entry.content, entry.knowledge_type.value, 
            entry.status.value, entry.author, json.dumps(entry.tags),
            entry.created_at.isoformat(), entry.updated_at.isoformat(),
            entry.version, entry.parent_id, entry.confidence_score,
            entry.usage_count, entry.effectiveness_rating, 
            json.dumps(entry.related_entries)
        ))
        
        conn.commit()
        conn.close()

    async def _enhance_knowledge_entry(self, entry_id: str):
        """Autonomously enhance knowledge entry"""
        try:
            entry = self.knowledge_base.get(entry_id)
            if not entry:
                return
            
            # Find related entries
            related_entries = await self._find_related_knowledge(entry)
            entry.related_entries = related_entries
            
            # Calculate confidence score based on content quality
            entry.confidence_score = await self._calculate_confidence_score(entry)
            
            # Update status if confidence is high
            if entry.confidence_score > 0.8:
                entry.status = KnowledgeStatus.VERIFIED
            elif entry.confidence_score > 0.6:
                entry.status = KnowledgeStatus.ACTIVE
            
            # Save enhanced entry
            await self._save_knowledge_entry(entry)
            
        except Exception as e:
            self.logger.error(f"Failed to enhance knowledge entry {entry_id}: {e}")

    async def _find_related_knowledge(self, entry: KnowledgeEntry) -> List[str]:
        """Find related knowledge entries using AI patterns"""
        related = []
        
        # Simple keyword matching for now - can be enhanced with ML
        entry_keywords = set(entry.content.lower().split() + entry.tags)
        
        for other_id, other_entry in self.knowledge_base.items():
            if other_id == entry.id:
                continue
                
            other_keywords = set(other_entry.content.lower().split() + other_entry.tags)
            
            # Calculate similarity
            common_keywords = entry_keywords.intersection(other_keywords)
            similarity = len(common_keywords) / max(len(entry_keywords), len(other_keywords))
            
            if similarity > 0.3:  # Threshold for relatedness
                related.append(other_id)
        
        return related[:10]  # Limit to top 10 related entries

    async def _calculate_confidence_score(self, entry: KnowledgeEntry) -> float:
        """Calculate confidence score for knowledge entry"""
        score = 0.5  # Base score
        
        # Length factor
        if len(entry.content) > 100:
            score += 0.1
        if len(entry.content) > 500:
            score += 0.1
        
        # Tags factor
        if len(entry.tags) > 0:
            score += 0.1
        
        # Usage factor
        if entry.usage_count > 5:
            score += 0.2
        
        # Effectiveness factor
        if entry.effectiveness_rating > 0.7:
            score += 0.3
        
        return min(score, 1.0)

    async def start_learning_session(self, title: str, description: str, 
                                   participants: List[str]) -> str:
        """Start a collaborative learning session"""
        try:
            session_id = hashlib.sha256(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            session = LearningSession(
                id=session_id,
                title=title,
                description=description,
                participants=participants,
                knowledge_entries=[],
                created_at=datetime.now()
            )
            
            self.learning_sessions[session_id] = session
            
            # Save to database
            await self._save_learning_session(session)
            
            self.console.print(f"[green]🎓 Started learning session: {title}[/green]")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start learning session: {e}")
            raise

    async def _save_learning_session(self, session: LearningSession):
        """Save learning session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learning_sessions 
            (id, title, description, participants, knowledge_entries, created_at, status, 
             insights_generated, problems_solved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.id, session.title, session.description,
            json.dumps(session.participants), json.dumps(session.knowledge_entries),
            session.created_at.isoformat(), session.status,
            session.insights_generated, session.problems_solved
        ))
        
        conn.commit()
        conn.close()

    async def add_problem_context(self, problem_description: str, domain: str, 
                                 priority: int = 1) -> str:
        """Add problem context for autonomous solving"""
        try:
            context_id = hashlib.sha256(f"{problem_description}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            context = ProblemContext(
                id=context_id,
                problem_description=problem_description,
                domain=domain,
                priority=priority,
                created_at=datetime.now(),
                attempted_solutions=[]
            )
            
            self.problem_contexts[context_id] = context
            
            # Save to database
            await self._save_problem_context(context)
            
            # Trigger autonomous problem solving
            asyncio.create_task(self._solve_problem_autonomous(context_id))
            
            self.logger.info(f"Added problem context: {problem_description}")
            return context_id
            
        except Exception as e:
            self.logger.error(f"Failed to add problem context: {e}")
            raise

    async def _save_problem_context(self, context: ProblemContext):
        """Save problem context to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO problem_contexts 
            (id, problem_description, domain, priority, created_at, attempted_solutions, 
             status, confidence_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            context.id, context.problem_description, context.domain, context.priority,
            context.created_at.isoformat(), json.dumps(context.attempted_solutions),
            context.status, context.confidence_level
        ))
        
        conn.commit()
        conn.close()

    async def _solve_problem_autonomous(self, context_id: str):
        """Autonomously solve problem using knowledge base"""
        try:
            context = self.problem_contexts.get(context_id)
            if not context:
                return
            
            # Find relevant knowledge entries
            relevant_knowledge = await self._find_relevant_knowledge(context)
            
            # Generate solution based on knowledge
            solution = await self._generate_solution(context, relevant_knowledge)
            
            if solution:
                # Add solution to knowledge base
                solution_id = await self.add_knowledge(
                    title=f"Solution: {context.problem_description}",
                    content=solution,
                    knowledge_type=KnowledgeType.SOLUTION,
                    author="autonomous_solver",
                    tags=[context.domain, "autonomous", "solution"]
                )
                
                context.attempted_solutions.append(solution_id)
                context.status = "solution_generated"
                context.confidence_level = 0.7
                
                await self._save_problem_context(context)
                
                self.logger.info(f"Generated autonomous solution for: {context.problem_description}")
            
        except Exception as e:
            self.logger.error(f"Failed to solve problem autonomously: {e}")

    async def _find_relevant_knowledge(self, context: ProblemContext) -> List[KnowledgeEntry]:
        """Find knowledge entries relevant to problem context"""
        relevant = []
        
        # Simple keyword matching - can be enhanced with ML
        problem_keywords = set(context.problem_description.lower().split() + [context.domain])
        
        for entry in self.knowledge_base.values():
            entry_keywords = set(entry.content.lower().split() + entry.tags)
            
            # Calculate relevance
            common_keywords = problem_keywords.intersection(entry_keywords)
            relevance = len(common_keywords) / max(len(problem_keywords), len(entry_keywords))
            
            if relevance > 0.2:  # Threshold for relevance
                relevant.append(entry)
        
        # Sort by effectiveness and confidence
        relevant.sort(key=lambda x: (x.effectiveness_rating, x.confidence_score), reverse=True)
        
        return relevant[:5]  # Top 5 most relevant

    async def _generate_solution(self, context: ProblemContext, 
                               relevant_knowledge: List[KnowledgeEntry]) -> Optional[str]:
        """Generate solution based on relevant knowledge"""
        if not relevant_knowledge:
            return None
        
        # Simple solution generation - can be enhanced with AI
        solution_parts = []
        
        solution_parts.append(f"Problem: {context.problem_description}")
        solution_parts.append(f"Domain: {context.domain}")
        solution_parts.append("\nRelevant Knowledge:")
        
        for entry in relevant_knowledge:
            solution_parts.append(f"- {entry.title}: {entry.content[:200]}...")
        
        solution_parts.append(f"\nGenerated Solution:")
        solution_parts.append(f"Based on the relevant knowledge, here's an autonomous solution approach:")
        
        # Extract key insights from relevant knowledge
        key_insights = []
        for entry in relevant_knowledge:
            if entry.knowledge_type == KnowledgeType.SOLUTION:
                key_insights.append(f"Apply {entry.title} approach")
            elif entry.knowledge_type == KnowledgeType.PROCESS:
                key_insights.append(f"Follow {entry.title} process")
        
        solution_parts.extend(key_insights)
        
        return "\n".join(solution_parts)

    async def _autonomous_knowledge_optimization(self):
        """Continuous autonomous knowledge optimization"""
        while True:
            try:
                # Update knowledge effectiveness based on usage
                for entry in self.knowledge_base.values():
                    if entry.usage_count > 0:
                        # Calculate effectiveness based on usage patterns
                        effectiveness = min(entry.usage_count / 10.0, 1.0)
                        entry.effectiveness_rating = effectiveness
                        
                        # Update status based on effectiveness
                        if effectiveness > 0.8:
                            entry.status = KnowledgeStatus.VERIFIED
                        elif effectiveness > 0.6:
                            entry.status = KnowledgeStatus.ACTIVE
                        
                        await self._save_knowledge_entry(entry)
                
                # Update learning patterns
                await self._update_learning_patterns()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Autonomous optimization failed: {e}")
                await asyncio.sleep(60)

    async def _autonomous_problem_solving(self):
        """Continuous autonomous problem solving"""
        while True:
            try:
                # Find unsolved problems
                unsolved_problems = [
                    context for context in self.problem_contexts.values()
                    if context.status == "analyzing"
                ]
                
                # Sort by priority
                unsolved_problems.sort(key=lambda x: x.priority, reverse=True)
                
                # Attempt to solve highest priority problems
                for context in unsolved_problems[:3]:  # Limit to 3 at a time
                    await self._solve_problem_autonomous(context.id)
                
                await asyncio.sleep(180)  # Run every 3 minutes
                
            except Exception as e:
                self.logger.error(f"Autonomous problem solving failed: {e}")
                await asyncio.sleep(60)

    async def _collaborative_insight_generation(self):
        """Generate collaborative insights from learning sessions"""
        while True:
            try:
                # Analyze active learning sessions
                active_sessions = [
                    session for session in self.learning_sessions.values()
                    if session.status == "active"
                ]
                
                for session in active_sessions:
                    # Generate insights based on session knowledge
                    insights = await self._generate_session_insights(session)
                    
                    if insights:
                        session.insights_generated += len(insights)
                        await self._save_learning_session(session)
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Collaborative insight generation failed: {e}")
                await asyncio.sleep(60)

    async def _generate_session_insights(self, session: LearningSession) -> List[str]:
        """Generate insights from learning session"""
        insights = []
        
        # Get knowledge entries from session
        session_knowledge = [
            self.knowledge_base[entry_id] 
            for entry_id in session.knowledge_entries
            if entry_id in self.knowledge_base
        ]
        
        if len(session_knowledge) > 1:
            # Find patterns across session knowledge
            common_tags = set()
            for entry in session_knowledge:
                common_tags.update(entry.tags)
            
            # Generate insights based on common patterns
            if common_tags:
                insight = f"Session insight: Common themes include {', '.join(list(common_tags)[:3])}"
                insights.append(insight)
                
                # Add insight to knowledge base
                await self.add_knowledge(
                    title=f"Session Insight: {session.title}",
                    content=insight,
                    knowledge_type=KnowledgeType.INSIGHT,
                    author="collaborative_generator",
                    tags=["insight", "collaborative", "session"]
                )
        
        return insights

    async def _update_learning_patterns(self):
        """Update learning patterns based on system behavior"""
        # Update solution effectiveness patterns
        solution_effectiveness = {}
        for entry in self.knowledge_base.values():
            if entry.knowledge_type == KnowledgeType.SOLUTION:
                solution_effectiveness[entry.id] = entry.effectiveness_rating
        
        self.learning_patterns['solution_effectiveness']['success_rates'] = solution_effectiveness
        
        # Save patterns to database
        await self._save_learning_patterns()

    async def _save_learning_patterns(self):
        """Save learning patterns to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern_type, pattern_data in self.learning_patterns.items():
            cursor.execute('''
                INSERT OR REPLACE INTO learning_patterns 
                (id, pattern_type, pattern_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                pattern_type, pattern_type, json.dumps(pattern_data),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()

    async def search_knowledge(self, query: str, knowledge_type: Optional[KnowledgeType] = None) -> List[KnowledgeEntry]:
        """Search knowledge base"""
        results = []
        query_words = set(query.lower().split())
        
        for entry in self.knowledge_base.values():
            # Skip if type filter doesn't match
            if knowledge_type and entry.knowledge_type != knowledge_type:
                continue
            
            # Calculate relevance score
            content_words = set(entry.content.lower().split())
            tag_words = set(entry.tags)
            title_words = set(entry.title.lower().split())
            
            all_words = content_words.union(tag_words).union(title_words)
            
            relevance = len(query_words.intersection(all_words)) / len(query_words)
            
            if relevance > 0.3:  # Threshold for relevance
                results.append(entry)
        
        # Sort by relevance and effectiveness
        results.sort(key=lambda x: (x.effectiveness_rating, x.confidence_score), reverse=True)
        
        return results

    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge sharing system statistics"""
        stats = {
            'total_knowledge_entries': len(self.knowledge_base),
            'active_learning_sessions': len([s for s in self.learning_sessions.values() if s.status == 'active']),
            'pending_problems': len([p for p in self.problem_contexts.values() if p.status == 'analyzing']),
            'solved_problems': len([p for p in self.problem_contexts.values() if p.status == 'solution_generated']),
            'knowledge_by_type': {},
            'knowledge_by_status': {},
            'average_confidence': 0.0,
            'total_insights_generated': sum(s.insights_generated for s in self.learning_sessions.values())
        }
        
        # Calculate knowledge by type and status
        for entry in self.knowledge_base.values():
            # By type
            type_key = entry.knowledge_type.value
            stats['knowledge_by_type'][type_key] = stats['knowledge_by_type'].get(type_key, 0) + 1
            
            # By status
            status_key = entry.status.value
            stats['knowledge_by_status'][status_key] = stats['knowledge_by_status'].get(status_key, 0) + 1
        
        # Calculate average confidence
        if self.knowledge_base:
            stats['average_confidence'] = sum(e.confidence_score for e in self.knowledge_base.values()) / len(self.knowledge_base)
        
        return stats

    def display_knowledge_stats(self):
        """Display knowledge sharing statistics"""
        try:
            stats = asyncio.run(self.get_knowledge_stats())
            
            # Create main stats table
            table = Table(title="Knowledge Sharing System Status", style="cyan")
            table.add_column("Metric", style="green")
            table.add_column("Value", style="yellow")
            table.add_column("Details", style="magenta")
            
            table.add_row("Total Knowledge", str(stats['total_knowledge_entries']), "Entries in knowledge base")
            table.add_row("Active Sessions", str(stats['active_learning_sessions']), "Collaborative learning sessions")
            table.add_row("Pending Problems", str(stats['pending_problems']), "Problems being analyzed")
            table.add_row("Solved Problems", str(stats['solved_problems']), "Autonomous solutions generated")
            table.add_row("Average Confidence", f"{stats['average_confidence']:.2f}", "Knowledge reliability score")
            table.add_row("Total Insights", str(stats['total_insights_generated']), "Collaborative insights generated")
            
            self.console.print(table)
            
            # Display knowledge by type
            if stats['knowledge_by_type']:
                type_table = Table(title="Knowledge by Type", style="green")
                type_table.add_column("Type", style="cyan")
                type_table.add_column("Count", style="yellow")
                
                for ktype, count in stats['knowledge_by_type'].items():
                    type_table.add_row(ktype.title(), str(count))
                
                self.console.print(type_table)
            
        except Exception as e:
            self.logger.error(f"Failed to display knowledge stats: {e}")

    async def integrate_with_mesh_network(self, mesh_network):
        """Integrate with mesh networking system"""
        self.mesh_network = mesh_network
        
        # Setup knowledge sharing across mesh nodes
        if hasattr(mesh_network, 'add_service'):
            await mesh_network.add_service('knowledge_sharing', self._handle_mesh_knowledge_request)
        
        self.logger.info("Knowledge sharing integrated with mesh network")

    async def _handle_mesh_knowledge_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge sharing requests from mesh network"""
        try:
            request_type = request.get('type')
            
            if request_type == 'search':
                query = request.get('query', '')
                results = await self.search_knowledge(query)
                return {
                    'status': 'success',
                    'results': [asdict(entry) for entry in results[:10]]  # Limit to 10
                }
            
            elif request_type == 'add_knowledge':
                title = request.get('title', '')
                content = request.get('content', '')
                knowledge_type = KnowledgeType(request.get('knowledge_type', 'technical'))
                author = request.get('author', 'mesh_user')
                tags = request.get('tags', [])
                
                entry_id = await self.add_knowledge(title, content, knowledge_type, author, tags)
                return {
                    'status': 'success',
                    'entry_id': entry_id
                }
            
            elif request_type == 'get_stats':
                stats = await self.get_knowledge_stats()
                return {
                    'status': 'success',
                    'stats': stats
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown request type: {request_type}'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to handle mesh knowledge request: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Example usage and integration
async def main():
    """Example usage of knowledge sharing system"""
    # Initialize system
    knowledge_system = KnowledgeShareManager()
    await knowledge_system.initialize()
    
    # Add some sample knowledge
    await knowledge_system.add_knowledge(
        title="Resource Distribution Optimization",
        content="Optimize resource distribution by analyzing usage patterns and adjusting allocation algorithms based on real-time demand.",
        knowledge_type=KnowledgeType.TECHNICAL,
        author="system_admin",
        tags=["optimization", "resources", "algorithm"]
    )
    
    # Start collaborative learning session
    session_id = await knowledge_system.start_learning_session(
        title="System Optimization Workshop",
        description="Collaborative session to optimize system performance",
        participants=["user1", "user2", "autonomous_agent"]
    )
    
    # Add problem context for autonomous solving
    problem_id = await knowledge_system.add_problem_context(
        problem_description="System response time is too slow during peak usage",
        domain="performance",
        priority=3
    )
    
    # Display statistics
    knowledge_system.display_knowledge_stats()
    
    # Keep system running
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
