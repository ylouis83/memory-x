-- Medical Knowledge Graph Database Schema
-- 医疗知识图谱数据库设计

-- 疾病实体表
CREATE TABLE diseases (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20),                    -- ICD-10编码
    category VARCHAR(100),               -- 疾病分类
    severity VARCHAR(20),                -- 严重程度: mild/moderate/severe
    description TEXT,                    -- 疾病描述
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_disease_name (name),
    INDEX idx_disease_code (code),
    INDEX idx_disease_category (category)
);

-- 症状实体表
CREATE TABLE symptoms (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,                    -- 症状描述
    body_part VARCHAR(100),             -- 涉及身体部位
    intensity VARCHAR(20),              -- 症状强度: mild/moderate/severe
    duration_type VARCHAR(20),          -- 持续时间类型: acute/chronic
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symptom_name (name),
    INDEX idx_symptom_body_part (body_part)
);

-- 药品实体表
CREATE TABLE medicines (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),          -- 通用名
    brand_name VARCHAR(200),            -- 商品名
    dosage_form VARCHAR(50),            -- 剂型: tablet/capsule/injection
    strength VARCHAR(50),               -- 规格
    manufacturer VARCHAR(200),          -- 生产厂家
    drug_class VARCHAR(100),            -- 药物分类
    prescription_required BOOLEAN DEFAULT FALSE, -- 是否需要处方
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_medicine_name (name),
    INDEX idx_medicine_generic (generic_name),
    INDEX idx_medicine_class (drug_class)
);

-- 疾病-症状关系表（咨询关系）
CREATE TABLE disease_symptom_relations (
    id VARCHAR(50) PRIMARY KEY,
    disease_id VARCHAR(50) NOT NULL,
    symptom_id VARCHAR(50) NOT NULL,
    relation_type VARCHAR(20) DEFAULT 'CONSULT',
    source VARCHAR(50) NOT NULL,        -- 源头: online_consult/physical_exam/medical_record/literature
    confidence DECIMAL(3,2) DEFAULT 0.50, -- 置信度 0.00-1.00
    frequency INT DEFAULT 1,            -- 出现频次
    context TEXT,                       -- 上下文信息
    user_id VARCHAR(50),                -- 用户ID（个人化数据）
    session_id VARCHAR(50),             -- 会话ID
    severity_correlation VARCHAR(20),   -- 严重程度关联
    time_correlation VARCHAR(20),       -- 时间关联: before/during/after
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(id) ON DELETE CASCADE,
    INDEX idx_ds_disease (disease_id),
    INDEX idx_ds_symptom (symptom_id),
    INDEX idx_ds_source (source),
    INDEX idx_ds_user (user_id),
    INDEX idx_ds_confidence (confidence),
    UNIQUE KEY uk_disease_symptom_user (disease_id, symptom_id, user_id, source)
);

-- 疾病-药品关系表（治疗关系）
CREATE TABLE disease_medicine_relations (
    id VARCHAR(50) PRIMARY KEY,
    disease_id VARCHAR(50) NOT NULL,
    medicine_id VARCHAR(50) NOT NULL,
    relation_type VARCHAR(20) DEFAULT 'TREATMENT',
    source VARCHAR(50) NOT NULL,        -- 源头: online_consult/physical_exam/prescription/literature
    effectiveness VARCHAR(20),          -- 疗效: excellent/good/fair/poor/unknown
    dosage VARCHAR(100),                -- 用量
    frequency VARCHAR(50),              -- 用药频次
    duration VARCHAR(50),               -- 疗程
    administration_route VARCHAR(50),    -- 给药途径
    side_effects JSON,                  -- 副作用列表
    contraindications JSON,             -- 禁忌症
    user_id VARCHAR(50),                -- 用户ID（个人化数据）
    doctor_id VARCHAR(50),              -- 医生ID
    prescription_date DATE,             -- 处方日期
    treatment_outcome VARCHAR(20),      -- 治疗结果
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
    INDEX idx_dm_disease (disease_id),
    INDEX idx_dm_medicine (medicine_id),
    INDEX idx_dm_source (source),
    INDEX idx_dm_user (user_id),
    INDEX idx_dm_effectiveness (effectiveness),
    UNIQUE KEY uk_disease_medicine_user (disease_id, medicine_id, user_id, prescription_date)
);

-- 图谱统计表
CREATE TABLE graph_statistics (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL,   -- diseases/symptoms/medicines
    total_count INT DEFAULT 0,
    active_relations INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stats_type (entity_type)
);

-- 用户图谱视图表（个人化知识图谱）
CREATE TABLE user_graph_views (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    entity_type VARCHAR(20) NOT NULL,   -- diseases/symptoms/medicines
    entity_id VARCHAR(50) NOT NULL,
    relevance_score DECIMAL(3,2) DEFAULT 0.50, -- 相关性评分
    access_frequency INT DEFAULT 1,     -- 访问频次
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_personal BOOLEAN DEFAULT TRUE,   -- 是否为个人数据
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_graph_user (user_id),
    INDEX idx_user_graph_entity (entity_type, entity_id),
    INDEX idx_user_graph_relevance (relevance_score),
    UNIQUE KEY uk_user_entity (user_id, entity_type, entity_id)
);

-- 创建初始统计数据
INSERT INTO graph_statistics (id, entity_type, total_count) VALUES 
('stat_diseases', 'diseases', 0),
('stat_symptoms', 'symptoms', 0),
('stat_medicines', 'medicines', 0);