import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# 殖民地模板
COLONY_TYPES = ["普通恒星系", "中子星", "黑洞", "大质量黑洞"]
COLONY_TEMPLATE = {
    "type": "普通恒星系",
    "resources": {
        "铁": 0,
        "纳米材料": 0,
        "能量": 0,
        "氢气": 0,
        "反氢气": 0,
        "星金": 0,
        "碳块": 0,
        "致密中子": 0,
        "强互作用力": 0
    },
    "buildings": {},
    "fleets": [],
    "research_count": 0,
    "ships": {  # 修改为字典，记录飞船的模块状态
        "ship_id": {
            "count": 1,  # 飞船数量
            "active_hydrogen": 0,  # 激活的采氢模块数量
            "active_stargold": 0,  # 激活的采星金模块数量
            "destroyer_used": False  # 歼星模块是否已使用
        }
    }
}

# 初始化数据结构
DEFAULT_DATA = {
    "current_colony": 0,
    "day": 1,  # 新增天数
    "log_entries": [],  # 新增日志
    "colonies": [
        {
            "name": "主基地",
            **COLONY_TEMPLATE,
            "resources": {
                "铁": 100,
                "纳米材料": 10,
                "能量": 50,
                "氢气": 5,
                **{k:0 for k in COLONY_TEMPLATE["resources"] if k not in ["铁", "纳米材料", "能量", "氢气"]}
            },
            "ships": {}  # 添加这一行
        }
    ],
    "fleets":[]
}

# 建筑配置
BUILDING_CONFIG = {
    # ...（保持原有建筑配置不变）
    "矿场": {
        "cost": {"铁": 1, "能量": 1},
        "output": {"铁": 1},
        "consumption": {},
        "location_type": "类地行星"
    },
    "纳米矿场": {
        "cost": {"纳米材料": 1, "能量": 1},
        "output": {"铁": 3},
        "consumption": {"能量": 3},
        "location_type": "类地行星"
    },
    "太阳能板": {
        "cost": {"铁": 1, "能量": 1},
        "output": {"能量": 1},
        "consumption": {},
        "location_type": "普通恒星/中子星"
    },
    "聚变反应堆": {
        "cost": {"铁": 5, "能量": 5},
        "output": {"能量": 10},
        "consumption": {"氢气": 1},
        "location_type": "任意"
    },
    "真空零点矿井":{
        "cost":{"铁":2000,"能量":2000},
        "output":{"能量":1000},
        "consumption":{},
        "location_type":"任意"
    },
    "戴森云":{
        "cost":{"碳块":500,"能量":5000},
        "output":{"反氢气":100},
        "consumption":{},
        "location_type":"普通恒星系"
    },
    "戴森环":{
        "cost":{"碳块":2500,"能量":25000},
        "output":{"反氢气":500},
        "consumption":{},
        "location_type":"普通恒星系"
    },
    "戴森球":{
        "cost":{"碳块":5000,"能量":50000},
        "output":{"反氢气":1000},
        "consumption":{},
        "location_type":"普通恒星系"
    },
    "研究站": {
        "cost": {"铁": 5, "能量": 2},
        "output": {},
        "consumption": {"能量": 2},
        "location_type": "科研中心"
    },
    "采氢气模块": {
        "cost": {},
        "output": {"氢气": 1},
        "consumption": {"能量": 1},
        "location_type": "任意恒星系"
    },
    "采星金模块": {
        "cost": {},
        "output": {"星金": 1},
        "consumption": {"能量": 1},
        "location_type": "任意恒星系"
    }
}

# 新增资源转换配置
CONVERSION_RULES = {
    "铁 → 纳米材料": {"cost": {"铁": 2}, "output": {"纳米材料": 1}},
    "铁 → 碳块": {"cost": {"铁": 5}, "output": {"碳块": 1}},
    "铁 → 致密中子": {"cost": {"铁": 10}, "output": {"致密中子": 1}},
    "铁 → 强互作用力": {"cost": {"铁": 20}, "output": {"强互作用力": 1}},
    "反氢气 → 能量": {"cost": {"反氢气": 1, "氢气": 1}, "output": {"能量": 1000}},
    "能量 → 铁": {"cost": {"能量": 50000}, "output": {"铁": 1}}
}

# 新增设计模板配置
SHIP_DESIGN_CONFIG = {
    "飞船": {
        "cost_multiplier": 1,
        "base_materials": {"铁": 100, "能量": 50}  # 基础材料
    },
    "行星要塞": {
        "cost_multiplier": 10,
        "base_materials": {"铁": 1000, "能量": 500}
    },
    "机动要塞": {
        "cost_multiplier": 20,
        "base_materials": {"铁": 2000, "能量": 1000}
    },
    "中子星要塞": {
        "cost_multiplier": 40,
        "base_materials": {"铁": 4000, "能量": 2000}
    },
    "黑洞要塞": {
        "cost_multiplier": 50,
        "base_materials": {"铁": 5000, "能量": 2500}
    }
}

class ResourceConversionDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("资源转换")
        
        ttk.Label(master, text="转换类型:").grid(row=0, column=0, padx=5, pady=5)
        self.conversion_type = ttk.Combobox(master, values=list(CONVERSION_RULES.keys()))
        self.conversion_type.grid(row=0, column=1, padx=5)
        
        ttk.Label(master, text="数量:").grid(row=1, column=0, padx=5, pady=5)
        self.quantity = ttk.Entry(master)
        self.quantity.grid(row=1, column=1, padx=5)
        
        # 显示当前资源
        self.resource_labels = {}
        for i, res in enumerate(COLONY_TEMPLATE["resources"], 2):
            lbl = ttk.Label(master, text=f"{res}: {self.parent.get_current_colony()['resources'].get(res, 0)}")
            lbl.grid(row=i, column=0, columnspan=2, sticky="w")
            self.resource_labels[res] = lbl
        
        return self.conversion_type
    
    def validate(self):
        try:
            qty = int(self.quantity.get())
            if qty <= 0:
                raise ValueError
            return True
        except:
            messagebox.showerror("错误", "数量必须为正整数")
            return False
    
    def apply(self):
        rule = CONVERSION_RULES[self.conversion_type.get()]
        self.result = (rule, int(self.quantity.get()))

class ShipDesignDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="输入格式示例：铁:100, 能量:50").grid(row=6, columnspan=2)
        self.title("设计飞船/要塞")
        self.material_entries = {}
        
        ttk.Label(master, text="模板类型:").grid(row=0, column=0, padx=5, pady=5)
        self.type_combo = ttk.Combobox(master, values=list(SHIP_DESIGN_CONFIG.keys()))
        self.type_combo.grid(row=0, column=1, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.update_cost)
        
        ttk.Label(master, text="模块数量:").grid(row=1, column=0, padx=5, pady=5)
        self.modules = ttk.Entry(master)
        self.modules.grid(row=1, column=1, padx=5)
        
        ttk.Label(master, text="编号:").grid(row=2, column=0, padx=5, pady=5)
        self.ship_id = ttk.Entry(master)
        self.ship_id.grid(row=2, column=1, padx=5)
        
        self.cost_label = ttk.Label(master, text="材料: 0 | 能量: 0")
        self.cost_label.grid(row=3, columnspan=2)

        ttk.Label(master, text="材料配置（格式：材料名:数量）").grid(row=4, columnspan=2)
        self.materials_entry = ttk.Entry(master)
        self.materials_entry.grid(row=5, columnspan=2, sticky="ew")
        self.materials_entry.insert(0, "铁:100, 能量:50")  # 默认值

        ttk.Label(master, text="聚变模块:").grid(row=4, column=0)
        self.fusion = ttk.Entry(master)
        self.fusion.grid(row=4, column=1)
        
        ttk.Label(master, text="采氢模块:").grid(row=5, column=0)
        self.hydrogen = ttk.Entry(master)
        self.hydrogen.grid(row=5, column=1)
        
        ttk.Label(master, text="采星金模块:").grid(row=6, column=0)
        self.stargold = ttk.Entry(master)
        self.stargold.grid(row=6, column=1)
        
        ttk.Label(master, text="歼星模块:").grid(row=7, column=0)
        self.destroyer = ttk.Entry(master)
        self.destroyer.grid(row=7, column=1)

        return self.type_combo
    
    def update_cost(self, event=None):
        try:
            # 解析材料输入
            materials = {}
            for pair in self.materials_entry.get().split(','):
                res, qty = pair.strip().split(':')
                materials[res.strip()] = int(qty.strip())
                
            modules = int(self.modules.get())
            design_type = self.type_combo.get()
            multiplier = SHIP_DESIGN_CONFIG[design_type]["cost_multiplier"]
            
            # 计算各材料消耗
            cost = {res: (qty + 10 * modules) * multiplier for res, qty in materials.items()}
            cost_str = " | ".join([f"{k}:{v}" for k, v in cost.items()])
            self.cost_label.config(text=f"材料消耗: {cost_str}")
        except Exception as e:
            print("输入格式错误:", e)
    
    def validate(self):
        for entry in [self.fusion, self.hydrogen, self.stargold, self.destroyer]:
            val = entry.get()
            if val.strip() == "":  # 处理空输入，默认为0
                entry.insert(0, "0")
            try:
                val = int(entry.get())
                if val < 0:
                    raise ValueError
            except:
                messagebox.showerror("错误", "模块数量必须为非负整数")
                return False
        return True
    
    def apply(self):
        materials = {}
        for pair in self.materials_entry.get().split(','):
            res, qty = pair.strip().split(':')
            materials[res.strip()] = int(qty.strip())
        design_type = self.type_combo.get()
        modules = int(self.modules.get())
        ship_id = self.ship_id.get().strip()
        multiplier = SHIP_DESIGN_CONFIG[design_type]["cost_multiplier"]
        
        self.result = {
        "id": self.ship_id.get().strip(),
        "type": self.type_combo.get(),
        "modules": {
            "fusion": int(self.fusion.get()),  # 聚变模块数量
            "hydrogen": int(self.hydrogen.get()),  # 采氢模块数量
            "stargold": int(self.stargold.get()),  # 采星金模块数量
            "destroyer": int(self.destroyer.get())  # 歼星模块数量
        },
        "cost": {  # 动态材料配置
            res: (qty + 10 * modules) * multiplier 
            for res, qty in materials.items()
        }
    }

class GameData:
    def __init__(self, filename="game_data.json"):
        self.filename = filename
        self.data = self.load_data()
        if "ship_designs" not in self.data:  # 初始化设计模板
            self.data["ship_designs"] = []
    
    def load_data(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                # 数据迁移：为旧版数据添加type字段
                for fleet in data["fleets"]:
                    if "count" not in fleet:
                        fleet["count"] = 1
                if "day" not in data:
                    data["day"] = 1
                if "log_entries" not in data:
                    data["log_entries"] = []
                for colony in data["colonies"]:
                    if "type" not in colony:
                        colony["type"] = "普通恒星系"
                # 确保fleets字段存在
                if "fleets" not in data:
                    data["fleets"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return DEFAULT_DATA
    
    def save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)

class BuildingDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="建筑类型:").grid(row=0)
        ttk.Label(master, text="建造数量:").grid(row=1)
        
        self.building_type = ttk.Combobox(master, values=list(BUILDING_CONFIG.keys()))
        self.quantity = ttk.Entry(master)
        
        self.building_type.grid(row=0, column=1)
        self.quantity.grid(row=1, column=1)
        return self.building_type
    
    def validate(self):
        try:
            qty = int(self.quantity.get())
            if qty <= 0:
                raise ValueError
            return True
        except:
            messagebox.showerror("错误", "数量必须为正整数")
            return False
    
    def apply(self):
        self.result = (self.building_type.get(), int(self.quantity.get()))

class FleetDialog(simpledialog.Dialog):
    # ...（保持原有舰队对话框不变）
    def body(self, master):
        self.title("添加航线")
        ttk.Label(master, text="航线路径:").grid(row=0)
        ttk.Label(master, text="舰队型号:").grid(row=1)
        ttk.Label(master, text="飞船数量:").grid(row=2)  # 新增数量标签
        ttk.Label(master, text="携带物质（格式：铁:200 纳米材料:200）:").grid(row=3)
        ttk.Label(master, text="携带能量:").grid(row=4)
        ttk.Label(master, text="剩余天数:").grid(row=5)
        
        self.route = ttk.Entry(master)
        self.ship_type = ttk.Entry(master)
        self.ship_count = ttk.Entry(master)  # 新增数量输入框
        self.materials = ttk.Entry(master)
        self.energy = ttk.Entry(master)
        self.days = ttk.Entry(master)
        
        self.route.grid(row=0, column=1)
        self.ship_type.grid(row=1, column=1)
        self.ship_count.grid(row=2, column=1)  # 布局新输入框
        self.materials.grid(row=3, column=1)
        self.energy.grid(row=4, column=1)
        self.days.grid(row=5, column=1)
        
        # 设置默认值
        self.ship_count.insert(0, "1")
        return self.route
    
    def validate(self):
        try:
            count = int(self.ship_count.get() or 1)
            if count <= 0:
                raise ValueError("数量必须大于0")
            # 验证物质格式
            materials = {}
            if self.materials.get().strip():
                for pair in self.materials.get().split():
                    res, qty = pair.split(':')
                    if res not in COLONY_TEMPLATE["resources"]:
                        raise ValueError(f"无效资源: {res}")
                    materials[res] = int(qty)
            
            int(self.energy.get())
            float(self.days.get())
            return True
        except Exception as e:
            messagebox.showerror("错误", f"输入格式错误: {str(e)}")
            return False
    
    def apply(self):
        materials = {}
        if self.materials.get().strip():
            for pair in self.materials.get().split():
                res, qty = pair.split(':')
                materials[res] = int(qty)
                
        count = int(self.ship_count.get() or 1)
        self.result = {
            "count": count,
            "route": self.route.get(),
            "ship_type": self.ship_type.get(),
            "materials": materials,
            "energy": int(self.energy.get()),
            "remaining_days": float(self.days.get()),
            "status": "运输中",
            "from_colony": self.master.game_data.data["current_colony"]  # 记录出发殖民地
        }

class ColonyDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="殖民地名称:").grid(row=0)
        ttk.Label(master, text="殖民地类型:").grid(row=1)
        ttk.Label(master, text="初始资源:").grid(row=2, columnspan=2)
        
        self.name_entry = ttk.Entry(master)
        self.type_combo = ttk.Combobox(master, values=COLONY_TYPES, state="readonly")
        
        self.name_entry.grid(row=0, column=1, padx=5)
        self.type_combo.grid(row=1, column=1, padx=5)
        self.type_combo.current(0)  # 默认选择第一个选项
        
        self.res_entries = {}
        for i, res in enumerate(COLONY_TEMPLATE["resources"], 3):
            ttk.Label(master, text=f"{res}:").grid(row=i, column=0, sticky="e")
            self.res_entries[res] = ttk.Entry(master)
            self.res_entries[res].grid(row=i, column=1, padx=5)
            self.res_entries[res].insert(0, "0")
        
        return self.name_entry
    
    def validate(self):
        try:
            for res in self.res_entries.values():
                int(res.get())
            return True
        except ValueError:
            messagebox.showerror("错误", "资源值必须为整数")
            return False
    
    def apply(self):
        resources = {res: int(entry.get()) for res, entry in self.res_entries.items()}
        self.result = (
            self.name_entry.get(),
            self.type_combo.get(),  # 确保这里返回的是用户选择的类型
            resources
        )

class ResourceEditDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("编辑殖民地资源")
        self.res_entries = {}
        
        ttk.Label(master, text="资源类型").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(master, text="新数值").grid(row=0, column=1, padx=5, pady=2)
        
        for i, res in enumerate(COLONY_TEMPLATE["resources"], 1):
            ttk.Label(master, text=res).grid(row=i, column=0, sticky="e", padx=5)
            self.res_entries[res] = ttk.Entry(master)
            self.res_entries[res].grid(row=i, column=1, padx=5, pady=2)
        
        return self.res_entries[next(iter(self.res_entries))]
    
    def validate(self):
        try:
            for res, entry in self.res_entries.items():
                int(entry.get())
            return True
        except ValueError:
            messagebox.showerror("错误", "请输入有效整数")
            return False
    
    def apply(self):
        self.result = {res: int(entry.get()) for res, entry in self.res_entries.items()}

class ResearchDialog(simpledialog.Dialog):
    def body(self, master):
        self.max_stations = self.parent.get_current_colony()["buildings"].get("研究站", 0)
        ttk.Label(master, text=f"可用研究站: {self.max_stations}").grid(row=0)
        ttk.Label(master, text="研究数量:").grid(row=1)
        
        self.research_entry = ttk.Entry(master)
        self.research_entry.grid(row=1, column=1)
        return self.research_entry
    
    def validate(self):
        try:
            value = int(self.research_entry.get())
            if value < 0 or value > self.max_stations:
                messagebox.showerror("错误", f"研究数量需在0-{self.max_stations}之间")
                return False
            return True
        except ValueError:
            messagebox.showerror("错误", "请输入有效整数")
            return False
    
    def apply(self):
        self.result = int(self.research_entry.get())

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("星云记录本")
        self.geometry("800x600")
        self.game_data = GameData()

        # ------------ 先初始化Notebook ------------
        self.notebook = ttk.Notebook(self)
        self.res_tab = ttk.Frame(self.notebook)
        self.building_tab = ttk.Frame(self.notebook)
        self.fleet_tab = ttk.Frame(self.notebook)
        self.log_tab = ttk.Frame(self.notebook)  # 新增日志标签页

        # 添加所有标签页
        #self.notebook.pack(expand=True, fill="both")

        # 殖民地选择控件
        self.colony_frame = ttk.Frame(self)
        self.colony_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(self.colony_frame, text="当前殖民地:").pack(side="left")
        self.colony_combo = ttk.Combobox(self.colony_frame, state="readonly")
        self.colony_combo.pack(side="left", padx=5)
        self.colony_combo.bind("<<ComboboxSelected>>", self.switch_colony)

        ttk.Button(self.colony_frame, text="添加殖民地", command=self.add_colony).pack(side="left", padx=5)
        self.update_colony_list()

        self.day_frame = ttk.Frame(self.colony_frame)
        self.day_frame.pack(side="left", padx=10)
        ttk.Label(self.day_frame, text="当前天数:").pack(side="left")
        self.day_label = ttk.Label(self.day_frame, text="1")
        self.day_label.pack(side="left", padx=5)
        ttk.Button(self.day_frame, text="修改", command=self.edit_day).pack(side="left")

        # 添加日志标签页
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="日志")
        
        # 日志树状图
        self.log_tree = ttk.Treeview(self.log_tab, columns=("day", "action"), show="headings")
        self.log_tree.heading("day", text="天数")
        self.log_tree.column("day", width=80)
        self.log_tree.heading("action", text="操作记录")
        self.log_tree.pack(fill="both", expand=True)

        # 将“更新至下一天”按钮放到顶部
        self.update_btn = ttk.Button(self, text="更新至下一天", command=self.update_day)
        self.update_btn.pack(pady=10)

        # 主界面布局
        self.notebook = ttk.Notebook(self)
        self.res_tab = ttk.Frame(self.notebook)
        self.building_tab = ttk.Frame(self.notebook)
        self.fleet_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.res_tab, text="资源")
        self.notebook.add(self.building_tab, text="建筑")
        self.notebook.add(self.fleet_tab, text="航线")
        self.notebook.pack(expand=True, fill="both")

        # 新增建筑控件初始化部分
        self.building_controls = ttk.Frame(self.building_tab)
        self.building_controls.pack(pady=5, fill="x")
        ttk.Button(self.building_controls, text="新建建筑", command=self.add_building).pack(side="left", padx=5)
        ttk.Button(self.building_controls, text="拆除建筑", command=self.remove_building).pack(side="left", padx=5)
        self.building_tree = ttk.Treeview(self.building_tab, columns=("type", "location"), show="headings")
        self.building_tree.heading("type", text="类型")
        self.building_tree.heading("location", text="位置")
        self.building_tree.pack(fill="both", expand=True)

        ttk.Button(self.building_controls, text="设计飞船/要塞", command=self.design_ship).pack(side="left", padx=5)

        # 初始化航线页面控件
        self.fleet_controls = ttk.Frame(self.fleet_tab)
        self.fleet_controls.pack(pady=5, fill="x")
        
        ttk.Button(self.fleet_controls, text="添加航线", command=self.add_fleet).pack(side="left", padx=5)
        ttk.Button(self.fleet_controls, text="删除航线", command=self.remove_fleet).pack(side="left", padx=5)
        ttk.Button(self.fleet_controls, text="编辑航线", command=self.edit_fleet).pack(side="left", padx=5)
        
        self.fleet_tree = ttk.Treeview(self.fleet_tab, 
            columns=("route", "ship", "count", "cargo", "remaining", "status"),
            show="headings")
        self.fleet_tree.heading("count", text="数量")  # 新增列
        self.fleet_tree.column("count", width=60)
        self.fleet_tree.heading("route", text="航线")
        self.fleet_tree.heading("ship", text="舰队型号")
        self.fleet_tree.heading("cargo", text="携带资源")
        self.fleet_tree.heading("remaining", text="剩余天数")
        self.fleet_tree.heading("status", text="状态")  # 新增列标题
        self.fleet_tree.pack(fill="both", expand=True)

        

        # 资源标签页
        self.res_tab.grid_columnconfigure(0, weight=1)
        self.res_labels = {}
        self.research_controls = ttk.Frame(self.res_tab)
        self.research_controls.grid(row=len(COLONY_TEMPLATE["resources"])+2, column=0, pady=5)
        
        ttk.Button(self.research_controls, text="设置研究数量", 
                 command=self.set_research).pack(side="left", padx=5)
        self.research_label = ttk.Label(self.research_controls, text="当前研究: 0/0")
        self.research_label.pack(side="left", padx=5)
        for i, res in enumerate(COLONY_TEMPLATE["resources"]):
            lbl = ttk.Label(self.res_tab, text=f"{res}: 0")
            lbl.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            self.res_labels[res] = lbl
        # 在资源标签页添加修改按钮
        self.res_controls = ttk.Frame(self.res_tab)
        self.res_controls.grid(row=len(COLONY_TEMPLATE["resources"])+1, column=0, pady=10)
        
        ttk.Button(self.res_controls, text="修改资源", command=self.edit_resources).pack()

        self.update_btn = ttk.Button(self, text="更新至下一天", command=self.update_day)
        self.update_btn.pack(pady=10)

        self.res_controls = ttk.Frame(self.res_tab)
        self.res_controls.grid(row=len(COLONY_TEMPLATE["resources"])+1, column=0, pady=10)
        
        ttk.Button(self.res_controls, text="修改资源", command=self.edit_resources).pack(side="left")
        ttk.Button(self.res_controls, text="资源转换", command=self.convert_resources).pack(side="left", padx=5)  # 新增按钮

        self.ship_frame = ttk.Frame(self.res_tab)
        self.ship_frame.grid(row=len(COLONY_TEMPLATE["resources"]) + 3, column=0, pady=10, sticky="ew")

        # 添加水平滚动条
        self.ship_canvas = tk.Canvas(self.ship_frame)
        self.ship_canvas.pack(side="left", fill="both", expand=True)

        self.ship_scroll = ttk.Scrollbar(self.ship_frame, orient="horizontal", command=self.ship_canvas.xview)
        self.ship_scroll.pack(side="bottom", fill="x")

        self.ship_canvas.configure(xscrollcommand=self.ship_scroll.set)
        self.ship_canvas.bind("<Configure>", lambda e: self.ship_canvas.configure(scrollregion=self.ship_canvas.bbox("all")))

        # 将飞船列表和按钮放在一个内部框架中
        self.ship_inner_frame = ttk.Frame(self.ship_canvas)
        self.ship_canvas.create_window((0, 0), window=self.ship_inner_frame, anchor="nw")

        ttk.Label(self.ship_inner_frame, text="已停靠飞船:").pack(side="left")
        self.ship_tree = ttk.Treeview(self.ship_inner_frame, columns=("id", "type", "count"), show="headings")
        self.ship_tree.heading("id", text="编号")
        self.ship_tree.heading("type", text="类型")
        self.ship_tree.heading("count", text="数量")
        self.ship_tree.pack(side="left", padx=5)
        self.ship_tree.bind("<<TreeviewSelect>>", lambda e: self.refresh_ship_buttons())

        ttk.Button(self.ship_inner_frame, text="建造", command=self.build_ship).pack(side="left", padx=5)
        ttk.Button(self.ship_inner_frame, text="修改数量", command=self.edit_ship_count).pack(side="left", padx=5)
        
        self.refresh_ui()

    def edit_day(self):
        new_day = simpledialog.askinteger("修改天数", "输入新天数:", minvalue=1)
        if new_day:
            old_day = self.game_data.data["day"]
            self.game_data.data["day"] = new_day
            self._add_log(f"天数修改：{old_day} → {new_day}")
            self.refresh_ui()

            self._add_log(f"天数修改：{old_day} → {new_day}")

    def _add_log(self, action):
        self.game_data.data["log_entries"].append({
            "day": self.game_data.data["day"],
            "action": action
        })
        self.game_data.save_data()

    def refresh_ship_buttons(self):
        # 清除旧按钮
        for child in self.ship_inner_frame.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text") in ["开始采氢", "停止采氢", "开始采星金", "停止采星金", "歼星"]:
                child.destroy()
    
        selected = self.ship_tree.selection()
        if not selected:
            return
    
        ship_id = self.ship_tree.item(selected[0])["values"][0]
        colony = self.get_current_colony()
        ship_data = colony["ships"].get(ship_id, {})
        design = next((d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id), None)
    
        if not design:
            return
    
        # 生成按钮
        btns = []
        if design["modules"]["hydrogen"] > 0:
            active_h = ship_data.get("active_hydrogen", 0)
            btn_text = "停止采氢" if active_h > 0 else "开始采氢"
            btns.append((btn_text, self.toggle_hydrogen))
    
        if design["modules"]["stargold"] > 0:
            active_sg = ship_data.get("active_stargold", 0)
            btn_text = "停止采星金" if active_sg > 0 else "开始采星金"
            btns.append((btn_text, self.toggle_stargold))
    
        if design["modules"]["destroyer"] > 0 and not ship_data.get("destroyer_used", False):
            btns.append(("歼星", self.activate_destroyer))
    
        # 将按钮添加到界面右侧
        for text, cmd in btns:
            ttk.Button(self.ship_inner_frame, text=text, command=cmd).pack(side="left", padx=5)
    
    def activate_destroyer(self):
        colony = self.get_current_colony()
        selected = self.ship_tree.selection()
        if not selected: return
    
        ship_id = self.ship_tree.item(selected[0])["values"][0]
        design = next(d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id)
    
        if design["modules"]["destroyer"] == 0:
            return
    
        # 输入行星资源
        res = simpledialog.askstring("歼星目标", "输入资源格式：铁:数量 氢气:数量 星金:数量")
        try:
            resources = {k:int(v) for k,v in [pair.split(":") for pair in res.split()]}
        except:
            messagebox.showerror("格式错误", "示例：铁:5000 氢气:200 星金:100")
            return
    
        # 扣除能量并获取资源
        if colony["resources"]["能量"] >= 500:
            colony["resources"]["能量"] -= 500
            for res, qty in resources.items():
                colony["resources"][res] += qty // 2
            messagebox.showinfo("成功", f"获得资源：{ {k:v//2 for k,v in resources.items()} }")
        else:
            messagebox.showerror("能量不足", "需要500能量启动歼星模块")

    def edit_fleet(self):
        selected = self.fleet_tree.selection()
        if not selected: return
        index = self.fleet_tree.index(selected[0])
        fleet = self.game_data.data["fleets"][index]
        
        # 创建编辑对话框（可复用FleetDialog）
        dialog = FleetDialog(self)
        if dialog.result:
            # 保留出发殖民地信息
            dialog.result["from_colony"] = fleet["from_colony"]
            self.game_data.data["fleets"][index] = dialog.result
            self.game_data.save_data()
            self.refresh_ui()
    
    def design_ship(self):
        dialog = ShipDesignDialog(self)
        if dialog.result:
            self.game_data.data["ship_designs"].append(dialog.result)
            self.game_data.save_data()
            messagebox.showinfo("成功", "设计已保存")

            self._add_log(f"设计飞船/要塞：{dialog.result['id']}（类型：{dialog.result['type']}）")
    
    def build_ship(self):
        colony = self.get_current_colony()
        designs = self.game_data.data["ship_designs"]
        if not designs:
            messagebox.showerror("错误", "请先设计飞船/要塞")
            return

        # 选择设计
        design_dialog = simpledialog.askinteger("建造", "输入建造数量:", minvalue=1)
        if not design_dialog: return

        # 选择模板
        design = simpledialog.askstring("选择设计", "输入模板编号:")
        selected_design = next((d for d in designs if d["id"] == design), None)
        if not selected_design:
            messagebox.showerror("错误", "未找到该设计")
            return

        # 计算总消耗
        total_cost = {
            res: amount * design_dialog 
            for res, amount in selected_design["cost"].items()
        }

        # 检查资源
        for res, cost in selected_design["cost"].items():
            if colony["resources"].get(res, 0) < cost * design_dialog:
                messagebox.showerror("错误", f"{res}不足！需要{cost * design_dialog}")
                return

        # 扣除资源并添加飞船
        for res, cost in selected_design["cost"].items():
            colony["resources"][res] -= cost * design_dialog

        # 更新飞船列表（确保以字典形式存储）
        colony.setdefault("ships", {})
        current_data = colony["ships"].get(selected_design["id"], {"count": 0, "active_hydrogen": 0, "active_stargold": 0, "destroyer_used": False})
        current_data["count"] += design_dialog
        colony["ships"][selected_design["id"]] = current_data  # 更新为字典

        self.game_data.save_data()
        self.refresh_ui()

        self._add_log(f"建造飞船/要塞：{selected_design['id']} x{design_dialog}")
    
    def edit_ship_count(self):
        selected = self.ship_tree.selection()
        if not selected: return
        item = self.ship_tree.item(selected[0])
        ship_id = item["values"][0]
        
        new_count = simpledialog.askinteger("修改数量", f"新数量:", minvalue=0)
        if new_count is None: return
        
        colony = self.get_current_colony()
        if new_count == 0:
            del colony["ships"][ship_id]
        else:
            colony["ships"][ship_id] = new_count
        
        self.game_data.save_data()
        self.refresh_ui()
        
    def add_conversion_button(self):
        # 在资源标签页的修改按钮旁添加转换按钮
        ttk.Button(self.res_controls, text="资源转换", command=self.convert_resources).pack(side="left", padx=5)
    
    def convert_resources(self):
        colony = self.get_current_colony()
        dialog = ResourceConversionDialog(self)
        if not dialog.result: return
        
        rule, qty = dialog.result
        total_cost = {res: amount * qty for res, amount in rule["cost"].items()}
        total_output = {res: amount * qty for res, amount in rule["output"].items()}
        
        # 检查资源是否充足
        for res, cost in total_cost.items():
            if colony["resources"].get(res, 0) < cost:
                messagebox.showerror("错误", f"{res}不足！需要{cost}")
                return
        
        # 扣除资源并增加产出
        for res, cost in total_cost.items():
            colony["resources"][res] -= cost
        for res, output in total_output.items():
            colony["resources"][res] = colony["resources"].get(res, 0) + output
        
        self.game_data.save_data()
        self.refresh_ui()
        messagebox.showinfo("成功", "资源转换完成")

        self._add_log(f"资源转换：{rule} x{qty}")

    def set_research(self):
        colony = self.get_current_colony()
        dialog = ResearchDialog(self)
        if dialog.result is not None:
            colony["research_count"] = dialog.result
            self.game_data.save_data()
            self.refresh_ui()

        # 建筑标签页（保持原有结构）
        
        # 航线标签页（保持原有结构）
        
        # 更新按钮
        self.update_btn = ttk.Button(self, text="更新至下一天", command=self.update_day)
        self.update_btn.pack(pady=10)

        self.ship_tree.delete(*self.ship_tree.get_children())
        colony = self.get_current_colony()
        for ship_id, count in colony.get("ships", {}).items():
            design = next((d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id), None)
            if design:
                self.ship_tree.insert("", "end", values=(ship_id, design["type"], count))
        
        self.refresh_ui()

    def edit_resources(self):
        colony = self.get_current_colony()
        dialog = ResourceEditDialog(self)
        if not dialog.result: return
        
        # 更新资源数值
        for res, value in dialog.result.items():
            colony["resources"][res] = value
        
        self.game_data.save_data()
        self.refresh_ui()
        messagebox.showinfo("成功", "资源数值已更新")
    
    def get_current_colony(self):
        return self.game_data.data["colonies"][self.game_data.data["current_colony"]]
    
    def switch_colony(self, event=None):
        self.game_data.data["current_colony"] = self.colony_combo.current()
        self.refresh_ui()
    
    def update_colony_list(self):
        colonies = [colony["name"] for colony in self.game_data.data["colonies"]]
        self.colony_combo["values"] = colonies
        self.colony_combo.current(self.game_data.data["current_colony"])
    
    def add_colony(self):
        dialog = ColonyDialog(self)
        if not dialog.result: return

        name, colony_type, resources = dialog.result
        new_colony = {
            **COLONY_TEMPLATE,  # 先展开模板
            "name": name,
            "type": colony_type,  # 再覆盖type字段
            "resources": resources,
            "buildings": {},
            "ships": {}
        }
        self.game_data.data["colonies"].append(new_colony)
        self.game_data.data["current_colony"] = len(self.game_data.data["colonies"]) - 1
        self.game_data.save_data()
        self.update_colony_list()
        self.refresh_ui()

        self._add_log(f"新建殖民地：{name}（类型：{colony_type}）")
    
    def refresh_ui(self):
        self.day_label.config(text=str(self.game_data.data["day"]))
        
        # 更新日志显示
        self.log_tree.delete(*self.log_tree.get_children())
        for log in self.game_data.data["log_entries"]:
            self.log_tree.insert("", "end", values=(log["day"], log["action"]))

        colony = self.get_current_colony()
    
        # 更新殖民地名称显示
        self.colony_combo["values"] = [f"{c['name']} ({c['type']})" for c in self.game_data.data["colonies"]]
    
        # 更新资源显示
        for res, val in colony["resources"].items():
            self.res_labels[res].config(text=f"{res}: {val}")
    
        # 更新建筑列表
        self.building_tree.delete(*self.building_tree.get_children())
        for b_type, count in colony["buildings"].items():
            self.building_tree.insert("", "end", values=(b_type, f"x{count}"))
    
        # 更新航线列表
        self.fleet_tree.delete(*self.fleet_tree.get_children())
        for f in self.game_data.data["fleets"]:
            materials = " ".join([f"{k}:{v}" for k,v in f["materials"].items()])
            colony_name = self.game_data.data["colonies"][f["from_colony"]]["name"]
            self.fleet_tree.insert("", "end", values=(
                f"{colony_name} → {f['route']}",
                f["ship_type"],
                materials,
                f["energy"],
                f"{f['remaining_days']:.1f}天",
                f["status"]
            ))
    
        # 更新研究站显示
        stations = colony["buildings"].get("研究站", 0)
        self.research_label.config(
            text=f"当前研究: {colony['research_count']}/{stations}"
        )
    
        # 更新飞船列表
        self.ship_tree.delete(*self.ship_tree.get_children())
        for ship_id, ship_data in self.get_current_colony().get("ships", {}).items():
            # 数据迁移：如果旧数据是整数，转换为字典
            if isinstance(ship_data, int):
                ship_data = {
                    "count": ship_data,
                    "active_hydrogen": 0,
                    "active_stargold": 0,
                    "destroyer_used": False
                }
                self.get_current_colony()["ships"][ship_id] = ship_data
        
            design = next((d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id), None)
            if design:
                self.ship_tree.insert("", "end", values=(
                    ship_id,
                    design["type"],
                    ship_data["count"],
                    f"{ship_data.get('active_hydrogen', 0)}/{design['modules']['hydrogen']}",
                    f"{ship_data.get('active_stargold', 0)}/{design['modules']['stargold']}",
                    "已使用" if ship_data.get("destroyer_used", False) else "未使用"
                ))
    
        # 刷新操作按钮
        self.refresh_ship_buttons()

    def toggle_hydrogen(self):
        selected = self.ship_tree.selection()
        if not selected: return

        ship_id = self.ship_tree.item(selected[0])["values"][0]
        colony = self.get_current_colony()
        ship_data = colony["ships"][ship_id]
        design = next((d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id), None)

        # 计算最大可激活模块数 = 飞船数量 * 单船模块数
        max_h = ship_data["count"] * design["modules"]["hydrogen"]
        current_h = ship_data.get("active_hydrogen", 0)

        if current_h > 0:  # 停用所有模块
            ship_data["active_hydrogen"] = 0
        else:  # 激活模块
            qty = simpledialog.askinteger("激活采氢模块", 
                                    f"可激活模块数: {max_h}\n输入开启数量:", 
                                    minvalue=1, maxvalue=max_h)
            if qty:
                ship_data["active_hydrogen"] = qty

        self.game_data.save_data()
        self.refresh_ui()

    def toggle_stargold(self):
        selected = self.ship_tree.selection()
        if not selected: return

        ship_id = self.ship_tree.item(selected[0])["values"][0]
        colony = self.get_current_colony()
        ship_data = colony["ships"][ship_id]
        design = next((d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id), None)

        # 计算最大可激活模块数 = 飞船数量 * 单船模块数
        max_sg = ship_data["count"] * design["modules"]["stargold"]
        current_sg = ship_data.get("active_stargold", 0)

        if current_sg > 0:  # 停用所有模块
            ship_data["active_stargold"] = 0
        else:  # 激活模块
            qty = simpledialog.askinteger("激活采星金模块", 
                                    f"可激活模块数: {max_sg}\n输入开启数量:", 
                                    minvalue=1, maxvalue=max_sg)
            if qty:
                ship_data["active_stargold"] = qty

        self.game_data.save_data()
        self.refresh_ui()
    
    def add_building(self):
        colony = self.get_current_colony()
        dialog = BuildingDialog(self)
        if not dialog.result: return
    
        building_type, quantity = dialog.result
        config = BUILDING_CONFIG.get(building_type)
    
        # 类型检查（如太阳能板限制）
        if building_type == "太阳能板" and colony["type"] in ["黑洞", "大质量黑洞"]:
            messagebox.showerror("错误", "该星系无法建造太阳能板")
            return
    
        # 计算实际消耗
        cost_multiplier = 2 if colony["type"] in ["中子星", "黑洞", "大质量黑洞"] else 1
        total_cost = {
            res: (amount * cost_multiplier if res != "能量" else amount) * quantity
            for res, amount in config["cost"].items()
        }
    
        # 资源检查
        for res, cost in total_cost.items():
            if colony["resources"][res] < cost:
                messagebox.showerror("错误", f"{res}不足！需要{cost}")
                return
    
        # 扣除资源并添加建筑
        for res, cost in total_cost.items():
            colony["resources"][res] -= cost
    
        colony["buildings"][building_type] = colony["buildings"].get(building_type, 0) + quantity
        self.game_data.save_data()
        self.refresh_ui()

        self._add_log(f"建造建筑：{building_type} x{quantity}")

    
    def remove_building(self):
        selected = self.building_tree.selection()
        if not selected: return
    
        item = self.building_tree.item(selected[0])
        building_type = item["values"][0]
        current_count = self.get_current_colony()["buildings"].get(building_type, 0)
    
        # 获取拆除数量
        qty = simpledialog.askinteger("拆除建筑", 
                                    f"当前{building_type}数量: {current_count}\n输入拆除数量:",
                                    minvalue=1, maxvalue=current_count)
        if not qty: return
    
        # 计算返还资源
        config = BUILDING_CONFIG[building_type]
        cost_multiplier = 2 if self.get_current_colony()["type"] in ["中子星", "黑洞", "大质量黑洞"] else 1
        refund = {
            res: (cost * cost_multiplier if res != "能量" else cost) * qty // 2
            for res, cost in config["cost"].items()
        }
    
        # 更新数据
        self.get_current_colony()["buildings"][building_type] -= qty
        if self.get_current_colony()["buildings"][building_type] == 0:
            del self.get_current_colony()["buildings"][building_type]
    
        for res, amount in refund.items():
            self.get_current_colony()["resources"][res] += amount
    
        self.game_data.save_data()
        self.refresh_ui()

        self._add_log(f"拆除建筑：{building_type} x{qty}")
    
    def add_fleet(self):
        dialog = FleetDialog(self)
        if dialog.result:
            self.game_data.data["fleets"].append(dialog.result)
            self.game_data.save_data()
            self.refresh_ui()

            self._add_log(f"添加航线：{dialog.result['route']}（舰队：{dialog.result['ship_type']})")

    
    def remove_fleet(self):
        selected = self.fleet_tree.selection()
        if not selected: return
        index = self.fleet_tree.index(selected[0])
        del self.game_data.data["fleets"][index]
        self.game_data.save_data()
        self.refresh_ui()

        self._add_log(f"删除航线：{fleet['route']}（舰队：{fleet['ship_type']})")
    
    def update_day(self):
        self.game_data.data["day"] += 1
        self._add_log(f"天数推进至：{self.game_data.data['day']}")
        for colony in self.game_data.data["colonies"]:
        # ================= 处理建筑产出 =================
            has_dyson = "戴森球" in colony["buildings"]  # 新增判断
        
            for building_type, count in colony["buildings"].items():
                # 新增戴森球存在时不产生太阳能板能量
                if "戴森球" in colony["buildings"] and building_type == "太阳能板":
                    continue  # 跳过太阳能板产出
                
                config = BUILDING_CONFIG.get(building_type, {})
            
                # 计算总消耗和总产出
                total_consumption = {
                    res: amount * count 
                    for res, amount in config.get("consumption", {}).items()
                }
                total_output = {
                    res: amount * count 
                    for res, amount in config.get("output", {}).items()
                }

                # 检查是否满足消耗条件
                can_produce = True
                for res, req in total_consumption.items():
                    if colony["resources"].get(res, 0) < req:
                        can_produce = False
                        break

                if can_produce:
                    # 扣除消耗
                    for res, req in total_consumption.items():
                        colony["resources"][res] -= req
                    # 增加产出
                    for res, output in total_output.items():
                        colony["resources"][res] = colony["resources"].get(res, 0) + output
                
            # ================= 处理飞船模块 =================
        for ship_id, ship_data in colony.get("ships", {}).items():
            design = next((d for d in self.game_data.data["ship_designs"] if d["id"] == ship_id), None)
            if not design:
                continue

            ship_count = ship_data["count"]
            active_h = ship_data.get("active_hydrogen", 0)
            active_sg = ship_data.get("active_stargold", 0)

            # 采氢逻辑
            if active_h > 0:
                h_production = active_h  # 总氢气产量

                # 处理聚变模块（转换氢气为能量，无需消耗能量）
                fusion_per_ship = design["modules"]["fusion"]
                total_fusion = fusion_per_ship * ship_count
                fusion_used = min(h_production, total_fusion)
    
                # 聚变模块转换氢气为能量
                colony["resources"]["能量"] += fusion_used * 10  # 每单位转换10能量
                h_production -= fusion_used  # 剩余需通过能量采集的氢气

                # 处理剩余氢气的采集（每单位需1能量）
                if h_production > 0:
                    energy_needed = h_production
                    if colony["resources"]["能量"] >= energy_needed:
                        colony["resources"]["能量"] -= energy_needed
                        colony["resources"]["氢气"] += h_production
                    else:
                        # 能量不足时，尽可能采集
                        possible = colony["resources"]["能量"]
                        colony["resources"]["能量"] = 0
                        colony["resources"]["氢气"] += possible
                        h_production -= possible  # 记录未采集的部分（可选）

            # 采星金逻辑
            if active_sg > 0:
                cost = active_sg  # 每天消耗能量 = 激活模块数 * 1
                if colony["resources"]["能量"] >= cost:
                    colony["resources"]["能量"] -= cost
                    colony["resources"]["星金"] += active_sg  # 每天产量 = 激活模块数 * 1

            # ================= 处理舰队消耗 =================
        for fleet in self.game_data.data["fleets"]:
            if fleet["status"] != "运输中":
                continue
                                # 每日消耗能量（示例：每日消耗1%能量）
            count = fleet.get("count", 1)
        
             # 每日消耗 = 飞船数量 * 1
            daily_consumption = 1 * count
            if fleet["energy"] >= daily_consumption:
                fleet["energy"] -= daily_consumption
                fleet["remaining_days"] -= 1
            else:
                fleet["status"] = "能量耗尽"
        
            # ================= 处理研究消耗 =================
            research_cost = colony["research_count"] * 2
            if colony["resources"]["能量"] >= research_cost:
                colony["resources"]["能量"] -= research_cost
            else:
                messagebox.showwarning("能量不足", f"{colony['name']}研究所需能量不足，研究未进行")

        self.game_data.save_data()
        self.refresh_ui()

        self._add_log(f"天数推进至：{self.game_data.data['day']}")

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()