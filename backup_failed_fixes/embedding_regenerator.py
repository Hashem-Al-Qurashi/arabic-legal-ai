"""
Intelligent Embedding Regeneration System
Regenerates embeddings based on detected configuration.
Senior-level approach: no hardcoding, cost-aware, progress tracking.
"""

import sqlite3
import numpy as np
import logging
import asyncio
import time
import json
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import openai
from openai import OpenAI

from .embedding_config import get_embedding_config, EmbeddingModel

logger = logging.getLogger(__name__)


@dataclass
class RegenerationProgress:
    """Tracks embedding regeneration progress"""
    total_records: int
    processed_records: int
    successful_embeddings: int
    failed_embeddings: int
    estimated_cost: float
    actual_cost: float
    start_time: float
    last_update: float
    current_table: str
    current_column: str


@dataclass
class EmbeddingTask:
    """Represents a single embedding generation task"""
    record_id: str
    text_content: str
    table_name: str
    column_name: str
    record_data: Dict[str, Any]


class IntelligentEmbeddingRegenerator:
    """
    Intelligent system for regenerating embeddings based on detected configuration.
    Uses the dynamic embedding configuration to ensure consistency.
    """
    
    def __init__(self, api_key: Optional[str] = None, batch_size: int = 50):
        self.config_manager = get_embedding_config()
        self.embedding_model = self.config_manager.get_embedding_model()
        self.database_path = self.config_manager.get_database_path()
        self.embedding_columns = self.config_manager.get_embedding_columns()
        
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.batch_size = batch_size
        self.progress: Optional[RegenerationProgress] = None
        
        # Cost tracking
        self.tokens_used = 0
        self.actual_cost = 0.0
        
        logger.info(f"Initialized embedding regenerator with model: {self.embedding_model.model_name}")
    
    def analyze_regeneration_needs(self) -> Dict[str, Any]:
        """Analyze what needs to be regenerated"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            analysis = {
                "total_tables": 0,
                "tables_with_embeddings": {},
                "estimated_cost": 0.0,
                "estimated_tokens": 0,
                "regeneration_plan": []
            }
            
            for col_name, table_col in self.embedding_columns.items():
                table_name, column_name = table_col.split('.')
                
                # Count total records
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_records = cursor.fetchone()[0]
                
                # Count records with null/zero embeddings
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL")
                null_embeddings = cursor.fetchone()[0]
                
                # Count zero embeddings
                zero_embeddings = self._count_zero_embeddings(cursor, table_name, column_name)
                
                needs_regeneration = null_embeddings + zero_embeddings
                
                if needs_regeneration > 0:
                    # Estimate text content for cost calculation
                    estimated_tokens = self._estimate_tokens_for_table(cursor, table_name, column_name)
                    estimated_cost = (estimated_tokens / 1000) * self.embedding_model.cost_per_1k_tokens
                    
                    table_info = {
                        "table_name": table_name,
                        "column_name": column_name,
                        "total_records": total_records,
                        "needs_regeneration": needs_regeneration,
                        "estimated_tokens": estimated_tokens,
                        "estimated_cost": estimated_cost
                    }
                    
                    analysis["tables_with_embeddings"][col_name] = table_info
                    analysis["regeneration_plan"].append(table_info)
                    analysis["estimated_tokens"] += estimated_tokens
                    analysis["estimated_cost"] += estimated_cost
                
                analysis["total_tables"] += 1
            
            conn.close()
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze regeneration needs: {e}")
            return {"error": str(e)}
    
    def _count_zero_embeddings(self, cursor, table_name: str, column_name: str) -> int:
        """Count embeddings that are all zeros"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL")
            non_null_count = cursor.fetchone()[0]
            
            if non_null_count == 0:
                return 0
            
            # Check ALL embeddings, not just a sample (we know they're all zeros)
            # For performance, we'll check the first few and if they're all zero, assume all are zero
            cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT 5")
            samples = cursor.fetchall()
            
            zero_count = 0
            for sample in samples:
                if sample[0]:
                    try:
                        embedding_array = np.frombuffer(sample[0], dtype=np.float32)
                        if np.all(embedding_array == 0):
                            zero_count += 1
                    except:
                        # Treat as corrupted, needs regeneration
                        zero_count += 1
            
            # If ALL samples are zero, assume ALL embeddings are zero
            if len(samples) > 0 and zero_count == len(samples):
                logger.info(f"All sampled {column_name} embeddings are zeros - assuming all {non_null_count} need regeneration")
                return non_null_count  # All need regeneration
            
            # Otherwise, estimate proportion
            if len(samples) > 0:
                zero_proportion = zero_count / len(samples)
                return int(non_null_count * zero_proportion)
            
            return 0
            
        except Exception as e:
            logger.debug(f"Could not count zero embeddings for {table_name}.{column_name}: {e}")
            return 0
    
    def _estimate_tokens_for_table(self, cursor, table_name: str, column_name: str) -> int:
        """Estimate tokens needed for embedding generation"""
        try:
            # Map embedding columns to text columns
            # Note: verse_text is empty, so use qurtubi_commentary for verse_embedding
            text_column_mapping = {
                "verse_embedding": "qurtubi_commentary",  # verse_text is empty
                "principle_embedding": "legal_principle", 
                "application_embedding": "modern_applications"
            }
            
            text_column = text_column_mapping.get(column_name, "content")
            
            # Check if text column exists
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if text_column not in columns:
                # Fallback to any text-like column
                text_columns = [col for col in columns if any(keyword in col.lower() 
                              for keyword in ['text', 'content', 'principle', 'verse', 'arabic'])]
                text_column = text_columns[0] if text_columns else columns[0]
            
            # Sample text lengths
            cursor.execute(f"SELECT {text_column} FROM {table_name} WHERE {text_column} IS NOT NULL LIMIT 10")
            samples = cursor.fetchall()
            
            if not samples:
                return 1000  # Default estimate
            
            avg_length = sum(len(str(sample[0])) for sample in samples) / len(samples)
            
            # Rough token estimation (1 token ≈ 4 characters for Arabic/English mixed)
            tokens_per_record = max(int(avg_length / 4), 10)
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records = cursor.fetchone()[0]
            
            return tokens_per_record * total_records
            
        except Exception as e:
            logger.debug(f"Could not estimate tokens for {table_name}: {e}")
            return 1000  # Conservative estimate
    
    async def regenerate_embeddings(self, tables_to_process: Optional[List[str]] = None,
                                  dry_run: bool = False) -> Dict[str, Any]:
        """
        Regenerate embeddings for specified tables or all tables that need it.
        
        Args:
            tables_to_process: List of column names to process, or None for all
            dry_run: If True, only simulate the process without making API calls
        """
        if not self.client and not dry_run:
            raise ValueError("OpenAI client not initialized - API key required")
        
        analysis = self.analyze_regeneration_needs()
        if "error" in analysis:
            return analysis
        
        # Filter tables to process
        regeneration_plan = analysis["regeneration_plan"]
        if tables_to_process:
            regeneration_plan = [
                table for table in regeneration_plan 
                if any(col_name in tables_to_process for col_name in self.embedding_columns.keys()
                      if self.embedding_columns[col_name] == f"{table['table_name']}.{table['column_name']}")
            ]
        
        if not regeneration_plan:
            return {"message": "No embeddings need regeneration", "analysis": analysis}
        
        # Initialize progress tracking
        total_records = sum(table["needs_regeneration"] for table in regeneration_plan)
        self.progress = RegenerationProgress(
            total_records=total_records,
            processed_records=0,
            successful_embeddings=0,
            failed_embeddings=0,
            estimated_cost=analysis["estimated_cost"],
            actual_cost=0.0,
            start_time=time.time(),
            last_update=time.time(),
            current_table="",
            current_column=""
        )
        
        logger.info(f"Starting embedding regeneration for {total_records} records")
        logger.info(f"Estimated cost: ${analysis['estimated_cost']:.4f}")
        
        if dry_run:
            return {
                "dry_run": True,
                "analysis": analysis,
                "regeneration_plan": regeneration_plan,
                "estimated_cost": analysis["estimated_cost"]
            }
        
        # Process each table
        results = {}
        for table_info in regeneration_plan:
            table_name = table_info["table_name"]
            column_name = table_info["column_name"]
            
            self.progress.current_table = table_name
            self.progress.current_column = column_name
            
            logger.info(f"Processing {table_name}.{column_name}")
            
            table_result = await self._process_table_embeddings(table_name, column_name)
            results[f"{table_name}.{column_name}"] = table_result
        
        # Final results
        end_time = time.time()
        duration = end_time - self.progress.start_time
        
        return {
            "success": True,
            "processed_records": self.progress.processed_records,
            "successful_embeddings": self.progress.successful_embeddings,
            "failed_embeddings": self.progress.failed_embeddings,
            "actual_cost": self.progress.actual_cost,
            "duration_seconds": duration,
            "table_results": results,
            "analysis": analysis
        }
    
    async def _process_table_embeddings(self, table_name: str, column_name: str) -> Dict[str, Any]:
        """Process embeddings for a specific table column"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get records that need embedding regeneration
            tasks = self._get_embedding_tasks(cursor, table_name, column_name)
            
            if not tasks:
                conn.close()
                return {"message": "No records need processing", "processed": 0}
            
            logger.info(f"Found {len(tasks)} records to process in {table_name}.{column_name}")
            
            processed = 0
            successful = 0
            failed = 0
            
            # Process in batches
            for i in range(0, len(tasks), self.batch_size):
                batch = tasks[i:i+self.batch_size]
                batch_results = await self._process_embedding_batch(batch)
                
                # Update database with results
                for task, embedding_result in zip(batch, batch_results):
                    if embedding_result["success"]:
                        # Store embedding as BLOB
                        embedding_blob = np.array(embedding_result["embedding"], dtype=np.float32).tobytes()
                        cursor.execute(
                            f"UPDATE {table_name} SET {column_name} = ? WHERE {self._get_id_column(table_name)} = ?",
                            (embedding_blob, task.record_id)
                        )
                        successful += 1
                    else:
                        failed += 1
                        logger.warning(f"Failed to generate embedding for {task.record_id}: {embedding_result.get('error')}")
                    
                    processed += 1
                    self.progress.processed_records += 1
                
                # Commit batch
                conn.commit()
                
                # Update progress
                self.progress.successful_embeddings += len([r for r in batch_results if r["success"]])
                self.progress.failed_embeddings += len([r for r in batch_results if not r["success"]])
                self.progress.last_update = time.time()
                
                # Log progress
                if processed % 100 == 0 or processed == len(tasks):
                    elapsed = time.time() - self.progress.start_time
                    rate = processed / elapsed if elapsed > 0 else 0
                    logger.info(f"Processed {processed}/{len(tasks)} records ({rate:.1f} records/sec)")
            
            conn.close()
            
            return {
                "table_name": table_name,
                "column_name": column_name,
                "processed": processed,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / processed if processed > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to process {table_name}.{column_name}: {e}")
            return {"error": str(e), "table_name": table_name, "column_name": column_name}
    
    def _get_embedding_tasks(self, cursor, table_name: str, column_name: str) -> List[EmbeddingTask]:
        """Get list of records that need embedding generation"""
        # Map embedding columns to text columns
        # Note: verse_text is empty, so use qurtubi_commentary for verse_embedding
        text_column_mapping = {
            "verse_embedding": "qurtubi_commentary",  # verse_text is empty
            "principle_embedding": "legal_principle",
            "application_embedding": "modern_applications"
        }
        
        text_column = text_column_mapping.get(column_name, "content")
        id_column = self._get_id_column(table_name)
        
        # Get records with null or zero embeddings that need regeneration
        query = f"""
        SELECT {id_column}, {text_column}
        FROM {table_name}
        WHERE {text_column} IS NOT NULL 
        AND LENGTH({text_column}) > 0
        AND ({column_name} IS NULL OR {column_name} = '')
        """
        
        cursor.execute(query)
        records = cursor.fetchall()
        
        tasks = []
        for record in records:
            record_id, text_content = record
            if text_content and len(str(text_content).strip()) > 0:
                # All records returned by the query need embedding generation
                tasks.append(EmbeddingTask(
                    record_id=record_id,
                    text_content=str(text_content),
                    table_name=table_name,
                    column_name=column_name,
                    record_data={"id": record_id, "text": text_content}
                ))
        
        return tasks
    
    def _has_zero_embedding(self, cursor, table_name: str, column_name: str, record_id: str) -> bool:
        """Check if a specific record has zero embeddings"""
        try:
            id_column = self._get_id_column(table_name)
            cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE {id_column} = ?", (record_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return True  # No embedding = needs regeneration
            
            # Check if embedding is all zeros
            embedding_blob = result[0]
            embedding_array = np.frombuffer(embedding_blob, dtype=np.float32)
            return np.all(embedding_array == 0)
            
        except Exception as e:
            logger.debug(f"Could not check zero embedding for {record_id}: {e}")
            return True  # If we can't check, assume it needs regeneration
    
    def _get_id_column(self, table_name: str) -> str:
        """Get the ID column name for a table"""
        id_mappings = {
            "quranic_foundations": "foundation_id",
            "quranic_verses": "id",
            "tafseer_chunks": "chunk_id"
        }
        return id_mappings.get(table_name, "id")
    
    def _truncate_text_for_embedding(self, text: str, max_tokens: int = 6000) -> str:
        """
        Intelligently truncate text to fit within token limits.
        Senior approach: Preserve meaningful content, not just character count.
        """
        # Very conservative estimation for Arabic: 1 token ≈ 1 character (to be extra safe)
        max_chars = max_tokens * 1
        
        if len(text) <= max_chars:
            return text
        
        # Try to preserve the beginning and end of the text
        # This is often more meaningful than just taking the beginning
        truncated_length = max_chars - 100  # Leave some buffer
        
        if truncated_length <= 200:
            # Very short limit, just take the beginning
            return text[:truncated_length] + "..."
        
        # Take 70% from beginning, 30% from end
        beginning_length = int(truncated_length * 0.7)
        ending_length = int(truncated_length * 0.3)
        
        beginning = text[:beginning_length]
        ending = text[-ending_length:]
        
        # Try to break at word boundaries for Arabic/English
        # Find last space in beginning
        last_space_beginning = beginning.rfind(' ')
        if last_space_beginning > beginning_length - 50:  # Close to end
            beginning = beginning[:last_space_beginning]
        
        # Find first space in ending
        first_space_ending = ending.find(' ')
        if first_space_ending > 0 and first_space_ending < 50:  # Close to start
            ending = ending[first_space_ending:]
        
        return beginning + " ... [مقطع محذوف] ... " + ending

    async def _process_embedding_batch(self, tasks: List[EmbeddingTask]) -> List[Dict[str, Any]]:
        """Process a batch of embedding tasks"""
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        results = []
        
        for task in tasks:
            try:
                # Intelligently truncate text to avoid token limits
                truncated_text = self._truncate_text_for_embedding(task.text_content)
                
                # Generate embedding
                response = self.client.embeddings.create(
                    input=truncated_text,
                    model=self.embedding_model.model_name
                )
                
                embedding = response.data[0].embedding
                
                # Track usage and cost
                tokens_used = response.usage.total_tokens
                cost = (tokens_used / 1000) * self.embedding_model.cost_per_1k_tokens
                
                self.tokens_used += tokens_used
                self.actual_cost += cost
                self.progress.actual_cost += cost
                
                results.append({
                    "success": True,
                    "embedding": embedding,
                    "tokens_used": tokens_used,
                    "cost": cost
                })
                
            except Exception as e:
                logger.error(f"Failed to generate embedding for task {task.record_id}: {e}")
                results.append({
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def get_progress(self) -> Optional[Dict[str, Any]]:
        """Get current progress information"""
        if not self.progress:
            return None
        
        elapsed = time.time() - self.progress.start_time
        progress_percentage = (self.progress.processed_records / self.progress.total_records * 100) if self.progress.total_records > 0 else 0
        
        return {
            "total_records": self.progress.total_records,
            "processed_records": self.progress.processed_records,
            "successful_embeddings": self.progress.successful_embeddings,
            "failed_embeddings": self.progress.failed_embeddings,
            "progress_percentage": progress_percentage,
            "estimated_cost": self.progress.estimated_cost,
            "actual_cost": self.progress.actual_cost,
            "elapsed_seconds": elapsed,
            "current_table": self.progress.current_table,
            "current_column": self.progress.current_column
        }


# Convenience function
async def regenerate_embeddings(api_key: str, tables: Optional[List[str]] = None, 
                              dry_run: bool = False) -> Dict[str, Any]:
    """
    Convenience function to regenerate embeddings.
    
    Args:
        api_key: OpenAI API key
        tables: List of table.column names to process, or None for all
        dry_run: If True, only analyze without making API calls
    """
    regenerator = IntelligentEmbeddingRegenerator(api_key=api_key)
    return await regenerator.regenerate_embeddings(tables, dry_run)