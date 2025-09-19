#!/usr/bin/env python3
"""
医疗知识图谱管理器
Medical Knowledge Graph Manager

用于管理疾病、症状、药品三大实体及其关系的图谱存储系统
支持从用户在线问答中提取实体信息并构建知识图谱
"""

import os
import sqlite3
import json
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class SourceType(Enum):
    """数据源类型"""
    ONLINE_CONSULT = "online_consult"      # 在线咨询
    PHYSICAL_EXAM = "physical_exam"        # 体检
    MEDICAL_RECORD = "medical_record"      # 病历
    PRESCRIPTION = "prescription"          # 处方
    LITERATURE = "literature"              # 文献

class RelationType(Enum):
    """关系类型"""
    CONSULT = "CONSULT"        # 咨询关系（疾病-症状）
    TREATMENT = "TREATMENT"    # 治疗关系（疾病-药品）

@dataclass
class DiseaseEntity:
    """疾病实体"""
    id: str
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass  
class SymptomEntity:
    """症状实体"""
    id: str
    name: str
    description: Optional[str] = None
    body_part: Optional[str] = None
    intensity: Optional[str] = None
    duration_type: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass
class MedicineEntity:
    """药品实体"""
    id: str
    name: str
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    drug_class: Optional[str] = None
    prescription_required: bool = False
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass
class DiseaseSymptomRelation:
    """疾病-症状关系"""
    id: str
    disease_id: str
    symptom_id: str
    relation_type: str = RelationType.CONSULT.value
    source: str = SourceType.ONLINE_CONSULT.value
    confidence: float = 0.5
    frequency: int = 1
    context: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    severity_correlation: Optional[str] = None
    time_correlation: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

@dataclass
class DiseaseMedicineRelation:
    """疾病-药品关系"""
    id: str
    disease_id: str
    medicine_id: str
    relation_type: str = RelationType.TREATMENT.value
    source: str = SourceType.ONLINE_CONSULT.value
    effectiveness: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    administration_route: Optional[str] = None
    side_effects: Optional[List[str]] = None
    contraindications: Optional[List[str]] = None
    user_id: Optional[str] = None
    doctor_id: Optional[str] = None
    prescription_date: Optional[str] = None
    treatment_outcome: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

class MedicalGraphManager:
    """医疗知识图谱管理器"""
    _ENTITY_TABLE_MAP = {
        'disease': 'diseases',
        'symptom': 'symptoms',
        'medicine': 'medicines'
    }

    def __init__(self, db_path: str = "data/medical_graph.db"):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _connect(self):
        """Context manager wrapping sqlite connection with common pragmas and row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 3000")
        try:
            yield conn
            if conn.in_transaction:
                conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _ensure_timestamps(entity) -> Tuple[str, str]:
        """Ensure dataclass-like entity carries proper timestamps and return iso strings."""
        now = datetime.now()
        if getattr(entity, "created_time", None) is None:
            entity.created_time = now
        entity.updated_time = now
        return entity.created_time.isoformat(), entity.updated_time.isoformat()

    @staticmethod
    def _serialize_optional_json(value: Optional[List[Any]]) -> Optional[str]:
        """Serialize optional JSON fields while preserving existing string payloads."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def _deserialize_optional_json(value: Optional[str]) -> Optional[Any]:
        """Best-effort JSON deserialization that tolerates legacy plain strings."""
        if value in (None, ""):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    def _init_database(self):
        """初始化数据库"""
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        cursor = conn.cursor()

        # 直接创建基本表结构，不使用复杂的schema文件
        self._create_basic_tables(cursor)
        self._create_indexes(cursor)
        conn.commit()
        conn.close()
    
    def _create_basic_tables(self, cursor):
        """创建基本表结构"""
        # 创建疾病表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT,
                category TEXT,
                severity TEXT,
                description TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建症状表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptoms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                body_part TEXT,
                intensity TEXT,
                duration_type TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建药品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                generic_name TEXT,
                brand_name TEXT,
                dosage_form TEXT,
                strength TEXT,
                manufacturer TEXT,
                drug_class TEXT,
                prescription_required BOOLEAN DEFAULT 0,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建疾病-症状关系表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_symptom_relations (
                id TEXT PRIMARY KEY,
                disease_id TEXT NOT NULL,
                symptom_id TEXT NOT NULL,
                relation_type TEXT DEFAULT 'CONSULT',
                source TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                frequency INTEGER DEFAULT 1,
                context TEXT,
                user_id TEXT,
                session_id TEXT,
                severity_correlation TEXT,
                time_correlation TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (disease_id) REFERENCES diseases(id),
                FOREIGN KEY (symptom_id) REFERENCES symptoms(id)
            )
        ''')
        
        # 创建疾病-药品关系表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_medicine_relations (
                id TEXT PRIMARY KEY,
                disease_id TEXT NOT NULL,
                medicine_id TEXT NOT NULL,
                relation_type TEXT DEFAULT 'TREATMENT',
                source TEXT NOT NULL,
                effectiveness TEXT,
                dosage TEXT,
                frequency TEXT,
                duration TEXT,
                administration_route TEXT,
                side_effects TEXT,
                contraindications TEXT,
                user_id TEXT,
                doctor_id TEXT,
                prescription_date TEXT,
                treatment_outcome TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (disease_id) REFERENCES diseases(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        ''')

    def _create_indexes(self, cursor):
        """创建常用查询的索引以提升检索性能"""
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_disease_symptom_disease_id
            ON disease_symptom_relations (disease_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_disease_symptom_symptom_id
            ON disease_symptom_relations (symptom_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_disease_symptom_user_source
            ON disease_symptom_relations (user_id, source)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_disease_medicine_disease_id
            ON disease_medicine_relations (disease_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_disease_medicine_medicine_id
            ON disease_medicine_relations (medicine_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_disease_medicine_user_source
            ON disease_medicine_relations (user_id, source)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_diseases_name
            ON diseases (name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symptoms_name
            ON symptoms (name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_medicines_name
            ON medicines (name)
        ''')

    def add_disease(self, disease: DiseaseEntity) -> bool:
        """添加疾病实体"""
        try:
            created_iso, updated_iso = self._ensure_timestamps(disease)
            with self._connect() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO diseases
                    (id, name, code, category, severity, description, created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    disease.id, disease.name, disease.code, disease.category,
                    disease.severity, disease.description, created_iso, updated_iso
                ))
            return True
        except Exception as e:
            print(f"添加疾病实体失败: {e}")
            return False

    def add_symptom(self, symptom: SymptomEntity) -> bool:
        """添加症状实体"""
        try:
            created_iso, updated_iso = self._ensure_timestamps(symptom)
            with self._connect() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO symptoms
                    (id, name, description, body_part, intensity, duration_type, created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symptom.id, symptom.name, symptom.description, symptom.body_part,
                    symptom.intensity, symptom.duration_type, created_iso, updated_iso
                ))
            return True
        except Exception as e:
            print(f"添加症状实体失败: {e}")
            return False

    def add_medicine(self, medicine: MedicineEntity) -> bool:
        """添加药品实体"""
        try:
            created_iso, updated_iso = self._ensure_timestamps(medicine)
            with self._connect() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO medicines
                    (id, name, generic_name, brand_name, dosage_form, strength,
                     manufacturer, drug_class, prescription_required, created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    medicine.id, medicine.name, medicine.generic_name, medicine.brand_name,
                    medicine.dosage_form, medicine.strength, medicine.manufacturer,
                    medicine.drug_class, medicine.prescription_required,
                    created_iso, updated_iso
                ))
            return True
        except Exception as e:
            print(f"添加药品实体失败: {e}")
            return False

    def add_disease_symptom_relation(self, relation: DiseaseSymptomRelation) -> bool:
        """添加疾病-症状关系"""
        try:
            created_iso, updated_iso = self._ensure_timestamps(relation)
            with self._connect() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO disease_symptom_relations
                    (id, disease_id, symptom_id, relation_type, source, confidence, frequency,
                     context, user_id, session_id, severity_correlation, time_correlation,
                     created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    relation.id, relation.disease_id, relation.symptom_id, relation.relation_type,
                    relation.source, relation.confidence, relation.frequency, relation.context,
                    relation.user_id, relation.session_id, relation.severity_correlation,
                    relation.time_correlation, created_iso, updated_iso
                ))
            return True
        except Exception as e:
            print(f"添加疾病-症状关系失败: {e}")
            return False

    def add_disease_medicine_relation(self, relation: DiseaseMedicineRelation) -> bool:
        """添加疾病-药品关系"""
        try:
            created_iso, updated_iso = self._ensure_timestamps(relation)
            side_effects_json = self._serialize_optional_json(relation.side_effects)
            contraindications_json = self._serialize_optional_json(relation.contraindications)

            with self._connect() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO disease_medicine_relations
                    (id, disease_id, medicine_id, relation_type, source, effectiveness,
                     dosage, frequency, duration, administration_route, side_effects,
                     contraindications, user_id, doctor_id, prescription_date,
                     treatment_outcome, created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    relation.id, relation.disease_id, relation.medicine_id, relation.relation_type,
                    relation.source, relation.effectiveness, relation.dosage, relation.frequency,
                    relation.duration, relation.administration_route, side_effects_json,
                    contraindications_json, relation.user_id, relation.doctor_id,
                    relation.prescription_date, relation.treatment_outcome,
                    created_iso, updated_iso
                ))
            return True
        except Exception as e:
            print(f"添加疾病-药品关系失败: {e}")
            return False

    def search_entities_by_name(self, entity_type: str, name: str) -> List[Dict]:
        """根据名称搜索实体"""
        table_name = self._ENTITY_TABLE_MAP.get(entity_type)
        if not table_name:
            return []
        
        with self._connect() as conn:
            cursor = conn.execute(f'''
                SELECT * FROM {table_name}
                WHERE name LIKE ?
                ORDER BY name
            ''', (f'%{name}%',))
            return [dict(row) for row in cursor.fetchall()]

    def get_disease_symptom_relations(self, user_id: str = None, source: str = None) -> List[Dict]:
        """获取疾病-症状关系"""
        query = '''
            SELECT dsr.*, d.name as disease_name, s.name as symptom_name
            FROM disease_symptom_relations dsr
            JOIN diseases d ON dsr.disease_id = d.id
            JOIN symptoms s ON dsr.symptom_id = s.id
            WHERE 1=1
        '''
        params: List[Any] = []

        if user_id:
            query += ' AND dsr.user_id = ?'
            params.append(user_id)

        if source:
            query += ' AND dsr.source = ?'
            params.append(source)

        query += ' ORDER BY dsr.confidence DESC, dsr.created_time DESC'

        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_disease_medicine_relations(self, user_id: str = None, source: str = None) -> List[Dict]:
        """获取疾病-药品关系"""
        query = '''
            SELECT dmr.*, d.name as disease_name, m.name as medicine_name
            FROM disease_medicine_relations dmr
            JOIN diseases d ON dmr.disease_id = d.id
            JOIN medicines m ON dmr.medicine_id = m.id
            WHERE 1=1
        '''
        params: List[Any] = []

        if user_id:
            query += ' AND dmr.user_id = ?'
            params.append(user_id)

        if source:
            query += ' AND dmr.source = ?'
            params.append(source)

        query += ' ORDER BY dmr.created_time DESC'

        with self._connect() as conn:
            cursor = conn.execute(query, params)
            results = []
            for row in cursor.fetchall():
                record = dict(row)
                record['side_effects'] = self._deserialize_optional_json(record.get('side_effects'))
                record['contraindications'] = self._deserialize_optional_json(record.get('contraindications'))
                results.append(record)
            return results

    def get_user_graph_summary(self, user_id: str) -> Dict:
        """获取用户图谱摘要"""
        summary = {
            'user_id': user_id,
            'disease_symptom_relations': 0,
            'disease_medicine_relations': 0,
            'unique_diseases': 0,
            'unique_symptoms': 0,
            'unique_medicines': 0,
            'data_sources': []
        }

        with self._connect() as conn:
            ds_count, ds_diseases, ds_symptoms = conn.execute('''
                SELECT COUNT(*), COUNT(DISTINCT disease_id), COUNT(DISTINCT symptom_id)
                FROM disease_symptom_relations
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
            summary['disease_symptom_relations'] = ds_count or 0

            dm_count, dm_diseases, dm_medicines = conn.execute('''
                SELECT COUNT(*), COUNT(DISTINCT disease_id), COUNT(DISTINCT medicine_id)
                FROM disease_medicine_relations
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
            summary['disease_medicine_relations'] = dm_count or 0

            summary['unique_diseases'] = max(ds_diseases or 0, dm_diseases or 0)
            summary['unique_symptoms'] = ds_symptoms or 0
            summary['unique_medicines'] = dm_medicines or 0

            sources = conn.execute('''
                SELECT DISTINCT source FROM (
                    SELECT source FROM disease_symptom_relations WHERE user_id = ?
                    UNION
                    SELECT source FROM disease_medicine_relations WHERE user_id = ?
                )
            ''', (user_id, user_id)).fetchall()
            summary['data_sources'] = [row['source'] for row in sources]

        return summary

    def remove_diabetes_related_graph_data(self, user_id: str = None) -> Dict[str, Any]:
        """删除图谱中关于糖尿病的全部数据"""
        removal_result = {
            "success": False,
            "removed_diseases": 0,
            "removed_symptoms": 0,
            "removed_medicines": 0,
            "removed_disease_symptom_relations": 0,
            "removed_disease_medicine_relations": 0,
            "errors": []
        }
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                # 1. 删除糖尿病相关的疾病-症状关系
                ds_delete_query = """
                    DELETE FROM disease_symptom_relations
                    WHERE (disease_id IN (
                        SELECT id FROM diseases WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%diabetes%'
                    ) OR symptom_id IN (
                        SELECT id FROM symptoms WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%胰岛素%'
                    ))
                """
                if user_id:
                    ds_delete_query += " AND user_id = ?"
                    cursor.execute(ds_delete_query, (user_id,))
                else:
                    cursor.execute(ds_delete_query)
                removal_result["removed_disease_symptom_relations"] = cursor.rowcount

                # 2. 删除糖尿病相关的疾病-药品关系
                dm_delete_query = """
                    DELETE FROM disease_medicine_relations
                    WHERE (disease_id IN (
                        SELECT id FROM diseases WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%diabetes%'
                    ) OR medicine_id IN (
                        SELECT id FROM medicines WHERE name LIKE '%胰岛素%' OR name LIKE '%二甲双胍%' OR name LIKE '%insulin%'
                    ))
                """
                if user_id:
                    dm_delete_query += " AND user_id = ?"
                    cursor.execute(dm_delete_query, (user_id,))
                else:
                    cursor.execute(dm_delete_query)
                removal_result["removed_disease_medicine_relations"] = cursor.rowcount

                # 3. 删除糖尿病相关的疾病实体
                disease_delete_query = "DELETE FROM diseases WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%diabetes%'"
                cursor.execute(disease_delete_query)
                removal_result["removed_diseases"] = cursor.rowcount

                # 4. 删除糖尿病相关的症状实体（谨慎删除，只删除明确的糖尿病症状）
                symptom_delete_query = "DELETE FROM symptoms WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖异常%'"
                cursor.execute(symptom_delete_query)
                removal_result["removed_symptoms"] = cursor.rowcount

                # 5. 删除糖尿病相关的药物实体
                medicine_delete_query = "DELETE FROM medicines WHERE name LIKE '%胰岛素%' OR name LIKE '%二甲双胍%' OR name LIKE '%insulin%'"
                cursor.execute(medicine_delete_query)
                removal_result["removed_medicines"] = cursor.rowcount

                removal_result["success"] = True

        except Exception as e:
            removal_result["errors"].append(str(e))
            print(f"删除图谱糖尿病数据失败: {e}")
        return removal_result
    
    def get_diabetes_related_data(self, user_id: str = None) -> Dict[str, Any]:
        """获取图谱中糖尿病相关的数据，用于删除前预览"""
        diabetes_data = {
            "diseases": [],
            "symptoms": [],
            "medicines": [],
            "disease_symptom_relations": [],
            "disease_medicine_relations": []
        }
        
        try:
            with self._connect() as conn:
                diabetes_data["diseases"] = [dict(row) for row in conn.execute("""
                    SELECT * FROM diseases
                    WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%diabetes%'
                """)]

                diabetes_data["symptoms"] = [dict(row) for row in conn.execute("""
                    SELECT * FROM symptoms
                    WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%'
                """)]

                diabetes_data["medicines"] = [dict(row) for row in conn.execute("""
                    SELECT * FROM medicines
                    WHERE name LIKE '%胰岛素%' OR name LIKE '%二甲双胍%' OR name LIKE '%insulin%'
                """)]

                ds_query = """
                    SELECT dsr.*, d.name as disease_name, s.name as symptom_name
                    FROM disease_symptom_relations dsr
                    JOIN diseases d ON dsr.disease_id = d.id
                    JOIN symptoms s ON dsr.symptom_id = s.id
                    WHERE (d.name LIKE '%糖尿病%' OR d.name LIKE '%血糖%' OR d.name LIKE '%diabetes%'
                           OR s.name LIKE '%糖尿病%' OR s.name LIKE '%血糖%')
                """
                dm_query = """
                    SELECT dmr.*, d.name as disease_name, m.name as medicine_name
                    FROM disease_medicine_relations dmr
                    JOIN diseases d ON dmr.disease_id = d.id
                    JOIN medicines m ON dmr.medicine_id = m.id
                    WHERE (d.name LIKE '%糖尿病%' OR d.name LIKE '%血糖%' OR d.name LIKE '%diabetes%'
                           OR m.name LIKE '%胰岛素%' OR m.name LIKE '%二甲双胍%' OR m.name LIKE '%insulin%')
                """

                if user_id:
                    ds_cursor = conn.execute(ds_query + " AND dsr.user_id = ?", (user_id,))
                    dm_cursor = conn.execute(dm_query + " AND dmr.user_id = ?", (user_id,))
                else:
                    ds_cursor = conn.execute(ds_query)
                    dm_cursor = conn.execute(dm_query)

                diabetes_data["disease_symptom_relations"] = [dict(row) for row in ds_cursor.fetchall()]
                diabetes_data["disease_medicine_relations"] = [dict(row) for row in dm_cursor.fetchall()]
                for record in diabetes_data["disease_medicine_relations"]:
                    record['side_effects'] = self._deserialize_optional_json(record.get('side_effects'))
                    record['contraindications'] = self._deserialize_optional_json(record.get('contraindications'))

        except Exception as e:
            print(f"获取糖尿病相关数据失败: {e}")
        
        return diabetes_data

    @staticmethod
    def generate_entity_id(entity_type: str, name: str) -> str:
        """生成实体ID"""
        return f"{entity_type}_{uuid.uuid5(uuid.NAMESPACE_DNS, name).hex[:8]}"
    
    @staticmethod
    def generate_relation_id(entity1_id: str, entity2_id: str, relation_type: str) -> str:
        """生成关系ID"""
        relation_key = f"{entity1_id}_{entity2_id}_{relation_type}"
        return f"rel_{uuid.uuid5(uuid.NAMESPACE_DNS, relation_key).hex[:8]}"
