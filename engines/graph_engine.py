"""
Knowledge Graph Engine
----------------------
ระบบจัดการความสัมพันธ์ระหว่างแนวคิด (Concept Mapping) แบบ Graph Database
ช่วยให้ระบบสามารถ "จดจำ" และ "อนุมาน" ความสัมพันธ์ใหม่ๆ ได้

Features:
1. Concept Nodes: โหนดแทนแนวคิด สูตร กฎ
2. Relationship Edges: เส้นเชื่อมแสดงความสัมพันธ์ (is_a, uses, depends_on, etc.)
3. Semantic Search: ค้นหาแบบความหมาย ไม่ใช่แค่ keyword
4. Inference Engine: อนุมานความสัมพันธ์ใหม่จาก existing graph
5. Goal-Knowledge Linking: เชื่อมโยงความรู้กับเป้าหมายผู้ใช้
"""

import json
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict


class ConceptNode:
    """โหนดแทนแนวคิดหรือความรู้"""
    
    def __init__(self, node_id: str, name: str, category: str, 
                 data: Dict[str, Any] = None):
        self.node_id = node_id
        self.name = name
        self.category = category  # formula, law, concept, procedure
        self.data = data or {}
        self.created_at = datetime.now().isoformat()
        self.connections: List[str] = []  # IDs of connected nodes
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "category": self.category,
            "data": self.data,
            "created_at": self.created_at,
            "connections": self.connections
        }


class Relationship:
    """ความสัมพันธ์ระหว่างสองโหนด"""
    
    def __init__(self, source_id: str, target_id: str, relation_type: str,
                 weight: float = 1.0, metadata: Dict = None):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type  # is_a, uses, depends_on, enables, etc.
        self.weight = weight  # ความแข็งแรงของความสัมพันธ์
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class KnowledgeGraphEngine:
    """เครื่องยนต์จัดการ Graph ความรู้"""
    
    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.relationships: List[Relationship] = []
        self.adjacency_list: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        
        # Relation types ที่รองรับ
        self.relation_types = [
            "is_a",           # A เป็นประเภทของ B
            "uses",           # A ใช้ B
            "depends_on",     # A ขึ้นอยู่กับ B
            "enables",        # A ทำให้เกิด B
            "part_of",        # A เป็นส่วนหนึ่งของ B
            "related_to",     # A เกี่ยวข้องกับ B
            "prerequisite",   # A เป็นพื้นฐานของ B
            "applies_to"      # A ใช้ได้กับ B
        ]
        
        # โหลดข้อมูลเริ่มต้น
        self._load_from_kb()
    
    def _load_from_kb(self):
        """โหลดความรู้จาก kb.json มาสร้างเป็น Graph"""
        try:
            with open('data/kb.json', 'r', encoding='utf-8') as f:
                kb = json.load(f)
            
            # เพิ่ม formulas
            for idx, formula in enumerate(kb.get("formulas", [])):
                node_id = f"formula_{idx}"
                self.add_node(
                    node_id=node_id,
                    name=formula.get("name", f"Formula_{idx}"),
                    category="formula",
                    data=formula
                )
            
            # เพิ่ม physics laws
            for idx, law in enumerate(kb.get("physics_laws", [])):
                node_id = f"law_{idx}"
                self.add_node(
                    node_id=node_id,
                    name=law.get("name", f"Law_{idx}"),
                    category="law",
                    data=law
                )
            
            # เพิ่ม logic rules
            for idx, rule in enumerate(kb.get("logic_rules", [])):
                node_id = f"rule_{idx}"
                self.add_node(
                    node_id=node_id,
                    name=rule.get("name", f"Rule_{idx}"),
                    category="rule",
                    data=rule
                )
            
            # สร้างความสัมพันธ์พื้นฐาน
            self._create_initial_relationships()
            
        except FileNotFoundError:
            print("Warning: kb.json not found. Starting with empty graph.")
        except json.JSONDecodeError:
            print("Warning: kb.json is invalid JSON. Starting with empty graph.")
    
    def _create_initial_relationships(self):
        """สร้างความสัมพันธ์เริ่มต้นระหว่างความรู้"""
        # ตัวอย่าง: สูตรฟิสิกส์มักใช้สูตรคณิตศาสตร์
        math_formulas = [n for n in self.nodes.values() if n.category == "formula"]
        physics_laws = [n for n in self.nodes.values() if n.category == "law"]
        
        for law in physics_laws:
            for formula in math_formulas:
                # ถ้า law มีคำว่า "calculate" หรือ "compute" ใน data
                if any(keyword in str(law.data).lower() for keyword in ["calculate", "compute", "formula"]):
                    self.add_relationship(
                        source_id=law.node_id,
                        target_id=formula.node_id,
                        relation_type="uses",
                        weight=0.7
                    )
        
        # เพิ่มความสัมพันธ์แบบ manual สำหรับข้อมูลที่มีอยู่
        # F = ma ใช้ basic arithmetic
        self._add_manual_relationships()
    
    def _add_manual_relationships(self):
        """เพิ่มความสัมพันธ์แบบ manual"""
        # ความสัมพันธ์พื้นฐานระหว่าง formulas
        relationships_to_add = [
            # Geometry formulas ใช้ arithmetic
            ("formula_0", "formula_9", "depends_on"),  # area_circle ใช้ quadratic
            ("formula_1", "formula_9", "depends_on"),  # circumference ใช้ quadratic
            ("formula_5", "formula_0", "depends_on"),  # volume_sphere ใช้ area_circle
            ("formula_7", "formula_0", "depends_on"),  # volume_cylinder ใช้ area_circle
            
            # Physics laws ใช้ formulas
            ("law_0", "formula_9", "uses"),  # force ใช้ arithmetic
            ("law_1", "formula_9", "uses"),  # velocity ใช้ arithmetic
            ("law_3", "formula_9", "uses"),  # kinetic_energy ใช้ arithmetic
            ("law_4", "formula_9", "uses"),  # potential_energy ใช้ arithmetic
            
            # Logic rules เป็นพื้นฐานของทุกอย่าง
            ("rule_0", "law_0", "prerequisite"),  # modus_ponens เป็นพื้นฐานของ force
            ("rule_0", "law_1", "prerequisite"),  # modus_ponens เป็นพื้นฐานของ velocity
        ]
        
        for source_id, target_id, rel_type in relationships_to_add:
            if source_id in self.nodes and target_id in self.nodes:
                self.add_relationship(source_id, target_id, rel_type, weight=0.8)
    
    def add_node(self, node_id: str, name: str, category: str, 
                 data: Dict[str, Any] = None) -> ConceptNode:
        """เพิ่มโหนดใหม่"""
        if node_id in self.nodes:
            return self.nodes[node_id]
        
        node = ConceptNode(node_id, name, category, data)
        self.nodes[node_id] = node
        return node
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relation_type: str, weight: float = 1.0,
                        metadata: Dict = None) -> Optional[Relationship]:
        """เพิ่มความสัมพันธ์ระหว่างโหนด"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        if relation_type not in self.relation_types:
            return None
        
        rel = Relationship(source_id, target_id, relation_type, weight, metadata)
        self.relationships.append(rel)
        
        # อัปเดต adjacency list
        self.adjacency_list[source_id].append((target_id, relation_type))
        self.nodes[source_id].connections.append(target_id)
        
        return rel
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> List[List[str]]:
        """หาเส้นทางระหว่างสองโหนด"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        paths = []
        queue = [(start_id, [start_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current == end_id:
                paths.append(path)
                continue
            
            for neighbor, _ in self.adjacency_list[current]:
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))
        
        return paths
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """ค้นหาแบบความหมาย (เบื้องต้นด้วย keyword matching)"""
        results = []
        query_lower = query.lower()
        
        for node in self.nodes.values():
            score = 0.0
            
            # คะแนนจากชื่อ
            if query_lower in node.name.lower():
                score += 0.5
            
            # คะแนนจาก category
            if query_lower in node.category.lower():
                score += 0.3
            
            # คะแนนจาก data
            for key, value in node.data.items():
                if query_lower in str(value).lower():
                    score += 0.2
            
            if score > 0:
                results.append({
                    "node": node.to_dict(),
                    "score": score
                })
        
        # เรียงตามคะแนน
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def infer_relationships(self) -> List[Dict]:
        """อนุมานความสัมพันธ์ใหม่จาก existing graph"""
        inferences = []
        
        # Copy adjacency_list เพื่อป้องกัน RuntimeError
        adjacency_copy = dict(self.adjacency_list)
        
        # Transitive inference: ถ้า A uses B และ B depends_on C แล้ว A อาจ depends_on C
        for node1_id, neighbors1 in adjacency_copy.items():
            for target1, rel1 in list(neighbors1):  # Copy list เพื่อความปลอดภัย
                if rel1 == "uses":
                    if target1 in adjacency_copy:
                        for target2, rel2 in list(adjacency_copy[target1]):
                            if rel2 == "depends_on":
                                # ตรวจสอบว่ายังไม่มี relationship นี้
                                exists = any(
                                    r.source_id == node1_id and 
                                    r.target_id == target2 and 
                                    r.relation_type == "depends_on"
                                    for r in self.relationships
                                )
                                
                                if not exists:
                                    inferences.append({
                                        "type": "transitive",
                                        "source": node1_id,
                                        "target": target2,
                                        "inferred_relation": "depends_on",
                                        "confidence": 0.6
                                    })
        
        return inferences
    
    def get_related_knowledge(self, node_id: str, depth: int = 2) -> List[Dict]:
        """ดึงความรู้ที่เกี่ยวข้องกับโหนดที่กำหนด"""
        if node_id not in self.nodes:
            return []
        
        related = []
        visited = set()
        queue = [(node_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_depth > depth or current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_id != node_id:
                related.append({
                    "node": self.nodes[current_id].to_dict(),
                    "distance": current_depth
                })
            
            for neighbor, rel_type in self.adjacency_list[current_id]:
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
        
        return related
    
    def link_to_goal(self, goal_keywords: List[str]) -> List[Dict]:
        """เชื่อมโยงความรู้กับเป้าหมายผู้ใช้"""
        relevant_nodes = []
        
        for keyword in goal_keywords:
            search_results = self.semantic_search(keyword, top_k=3)
            for result in search_results:
                if result not in relevant_nodes:
                    relevant_nodes.append(result)
        
        # เพิ่มความรู้ที่เกี่ยวข้อง
        expanded = []
        for item in relevant_nodes:
            node_id = item["node"]["node_id"]
            related = self.get_related_knowledge(node_id, depth=1)
            for rel in related:
                if rel not in expanded:
                    expanded.append(rel)
        
        return {
            "direct_matches": relevant_nodes,
            "related_knowledge": expanded,
            "total_relevant": len(relevant_nodes) + len(expanded)
        }
    
    def get_graph_stats(self) -> Dict:
        """สถิติของ Graph"""
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "categories": dict(defaultdict(int)),
            "avg_connections": sum(len(n.connections) for n in self.nodes.values()) / max(1, len(self.nodes))
        }
    
    def export_graph(self) -> Dict:
        """Export graph ทั้งหมด"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "exported_at": datetime.now().isoformat()
        }
    
    def save_to_file(self, filepath: str = "data/knowledge_graph.json"):
        """บันทึก graph ลงไฟล์"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_graph(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str = "data/knowledge_graph.json"):
        """โหลด graph จากไฟล์"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.nodes = {}
            self.relationships = []
            self.adjacency_list = defaultdict(list)
            
            for node_data in data.get("nodes", []):
                node = ConceptNode(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                    category=node_data["category"],
                    data=node_data.get("data", {})
                )
                node.created_at = node_data.get("created_at", datetime.now().isoformat())
                node.connections = node_data.get("connections", [])
                self.nodes[node.node_id] = node
            
            for rel_data in data.get("relationships", []):
                rel = Relationship(
                    source_id=rel_data["source_id"],
                    target_id=rel_data["target_id"],
                    relation_type=rel_data["relation_type"],
                    weight=rel_data.get("weight", 1.0),
                    metadata=rel_data.get("metadata", {})
                )
                self.relationships.append(rel)
                self.adjacency_list[rel.source_id].append((rel.target_id, rel.relation_type))
            
        except FileNotFoundError:
            print(f"Warning: {filepath} not found.")


# Test the engine
if __name__ == "__main__":
    engine = KnowledgeGraphEngine()
    
    print(f"📊 Graph Statistics:")
    stats = engine.get_graph_stats()
    print(f"  Total Nodes: {stats['total_nodes']}")
    print(f"  Total Relationships: {stats['total_relationships']}")
    
    # ทดสอบ semantic search
    print("\n🔍 Semantic Search: 'force'")
    results = engine.semantic_search("force")
    for result in results:
        print(f"  - {result['node']['name']} (score: {result['score']:.2f})")
    
    # ทดสอบ linking to goal
    print("\n🎯 Link to Goal: ['finance', 'investment']")
    linked = engine.link_to_goal(["finance", "investment"])
    print(f"  Direct matches: {len(linked['direct_matches'])}")
    print(f"  Related knowledge: {len(linked['related_knowledge'])}")
    
    # Save graph
    engine.save_to_file()
    print("\n💾 Graph saved to data/knowledge_graph.json")
