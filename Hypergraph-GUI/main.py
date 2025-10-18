"""
HyperLLM Multi-Agent System GUI
Main application with multi-language support
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import json
import os
import sys
import threading
import subprocess
from pathlib import Path
from PIL import Image, ImageTk
import glob

# Add parent directory to path to import HyperLLM modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LanguageSelector(tk.Toplevel):
    """Language selection dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Language / 选择语言 / 언어 선택")
        self.geometry("700x200")
        self.resizable(False, False)
        
        self.selected_language = None
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"700x200+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create language selection widgets"""
        # Title
        title_label = tk.Label(
            self, 
            text="Select Language / 选择语言 / 언어 선택",
            font=("Arial", 16, "bold"),
            pady=30
        )
        title_label.pack()
        
        # Language buttons - horizontal layout
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        languages = [
            ("English", "en", "🇬🇧"),
            ("中文", "zh", "🇨🇳"),
            ("한국어", "ko", "🇰🇷")
        ]
        
        for i, (name, code, flag) in enumerate(languages):
            btn = tk.Button(
                button_frame,
                text=f"{flag}\n{name}",
                font=("Arial", 12),
                width=12,
                height=3,
                command=lambda c=code: self._select_language(c),
                bg="#2196F3",
                fg="white",
                relief="raised",
                bd=3
            )
            btn.grid(row=0, column=i, padx=15, pady=5)
    
    def _select_language(self, lang_code):
        """Handle language selection"""
        self.selected_language = lang_code
        self.destroy()


class HyperLLMGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide main window initially
        
        # Load language configuration
        self.languages = self._load_languages()
        
        # Show language selector
        lang_selector = LanguageSelector(root)
        root.wait_window(lang_selector)
        
        self.current_language = lang_selector.selected_language or "en"
        
        # Show main window
        self.root.deiconify()
        
        # Configure main window
        self.root.title(self._t("title"))
        self.root.geometry("1200x800")
        
        # Generation state
        self.is_running = False
        self.generation_thread = None
        self.log_text = None
        
        # Create main UI
        self._create_menu()
        self._create_notebook()
        self._create_status_bar()
        
    def _load_languages(self):
        """Load language configuration from JSON"""
        lang_file = Path(__file__).parent / "languages.json"
        with open(lang_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _t(self, key):
        """Translate key to current language"""
        return self.languages.get(key, {}).get(self.current_language, key)
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Language menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language / 语言 / 언어", menu=lang_menu)
        lang_menu.add_command(label="English 🇬🇧", command=lambda: self._change_language("en"))
        lang_menu.add_command(label="中文 🇨🇳", command=lambda: self._change_language("zh"))
        lang_menu.add_command(label="한국어 🇰🇷", command=lambda: self._change_language("ko"))
    
    def _change_language(self, lang_code):
        """Change application language"""
        self.current_language = lang_code
        messagebox.showinfo("Info", "Please restart application to apply language change")
    
    def _create_notebook(self):
        """Create tabbed notebook interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.modeling_frame = ttk.Frame(self.notebook)
        self.parameters_frame = ttk.Frame(self.notebook)
        self.evaluation_frame = ttk.Frame(self.notebook)
        self.entity_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.modeling_frame, text=self._t("tab_modeling"))
        self.notebook.add(self.parameters_frame, text=self._t("tab_parameters"))
        self.notebook.add(self.evaluation_frame, text=self._t("tab_evaluation"))
        self.notebook.add(self.entity_frame, text=self._t("tab_entity"))
        
        # Populate tabs
        self._create_modeling_tab()
        self._create_parameters_tab()
        self._create_evaluation_tab()
        self._create_entity_tab()
    
    def _create_modeling_tab(self):
        """Create hypergraph modeling tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.modeling_frame, text=self._t("tab_modeling"), padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill='x')
        
        self.start_btn = tk.Button(
            btn_frame,
            text=self._t("start_generation"),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self._start_generation,
            height=2
        )
        self.start_btn.pack(side='left', padx=5, fill='x', expand=True)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text=self._t("stop_generation"),
            bg="#f44336",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self._stop_generation,
            height=2,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5, fill='x', expand=True)
        
        # Status display
        status_frame = ttk.LabelFrame(self.modeling_frame, text=self._t("status"), padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        status_grid = tk.Frame(status_frame)
        status_grid.pack(fill='x')
        
        # Phase
        tk.Label(status_grid, text=self._t("current_phase"), font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', padx=5)
        self.phase_label = tk.Label(status_grid, text=self._t("ready"), font=("Arial", 10), fg="blue")
        self.phase_label.grid(row=0, column=1, sticky='w', padx=5)
        
        # Hyperedges count
        tk.Label(status_grid, text=self._t("hyperedges_generated"), font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', padx=5)
        self.edges_label = tk.Label(status_grid, text="0", font=("Arial", 10))
        self.edges_label.grid(row=1, column=1, sticky='w', padx=5)
        
        # Progress bar
        tk.Label(status_grid, text=self._t("progress"), font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', padx=5)
        self.progress_bar = ttk.Progressbar(status_grid, mode='determinate', length=300)
        self.progress_bar.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Recent hyperedges
        edges_frame = ttk.LabelFrame(self.modeling_frame, text=self._t("recent_hyperedges"), padding=10)
        edges_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.edges_text = scrolledtext.ScrolledText(edges_frame, height=15, wrap='word')
        self.edges_text.pack(fill='both', expand=True)
        
        # Console log
        log_frame = ttk.LabelFrame(self.modeling_frame, text="Console Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap='word', bg="#1e1e1e", fg="#ffffff")
        self.log_text.pack(fill='both', expand=True)
    
    def _create_parameters_tab(self):
        """Create parameters configuration tab"""
        # API Configuration section
        api_frame = ttk.LabelFrame(self.parameters_frame, text=self._t("api_configuration"), padding=10)
        api_frame.pack(fill='x', padx=10, pady=5)
        
        # API Key
        tk.Label(api_frame, text=self._t("api_key"), font=("Arial", 10)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=40, show="*")
        api_key_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # API Base URL
        tk.Label(api_frame, text=self._t("api_base_url"), font=("Arial", 10)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.api_base_url_var = tk.StringVar()
        api_url_entry = tk.Entry(api_frame, textvariable=self.api_base_url_var, width=40)
        api_url_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Save API Config button
        tk.Button(
            api_frame,
            text=self._t("save_api_config"),
            command=self._save_api_config,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        ).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Load existing API config
        self._load_api_config()
        
        # Main parameters
        main_frame = ttk.LabelFrame(self.parameters_frame, text=self._t("tab_parameters"), padding=10)
        main_frame.pack(fill='x', padx=10, pady=5)
        
        params = [
            ("iterations", 10),
            ("groups_per_iteration", 5),
            ("max_members", 5),
            ("preferential_attachment", 0.85)
        ]
        
        self.param_vars = {}
        
        for i, (param, default) in enumerate(params):
            tk.Label(main_frame, text=self._t(param), font=("Arial", 10)).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            var = tk.StringVar(value=str(default))
            entry = tk.Entry(main_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky='w', padx=5, pady=5)
            self.param_vars[param] = var
            
            # Add info label for preferential attachment
            if param == "preferential_attachment":
                info_label = tk.Label(
                    main_frame, 
                    font=("Arial", 8),
                    fg="gray"
                )
                info_label.grid(row=i, column=2, sticky='w', padx=5)
        
        # Model selection
        tk.Label(main_frame, text=self._t("model_selection"), font=("Arial", 10)).grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.model_var = tk.StringVar(value="gpt-4")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, values=["gpt-3.5-turbo", "gpt-4", "gpt-4.1-nano"], state='readonly', width=13)
        model_combo.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # File selections
        file_frame = ttk.LabelFrame(self.parameters_frame, text="Files", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        files = [
            ("config_file", "Config File"),
            ("personas_file", "Personas File"),
            ("resume_directory", "Resume Directory")
        ]
        
        self.file_vars = {}
        
        for i, (key, label) in enumerate(files):
            tk.Label(file_frame, text=self._t(key), font=("Arial", 10)).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            var = tk.StringVar()
            entry = tk.Entry(file_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky='w', padx=5, pady=5)
            
            is_dir = key == "resume_directory"
            btn = tk.Button(
                file_frame,
                text=self._t("browse"),
                command=lambda v=var, d=is_dir: self._browse_file(v, d)
            )
            btn.grid(row=i, column=2, padx=5, pady=5)
            self.file_vars[key] = var
        
        # Agent parameters
        agent_frame = ttk.LabelFrame(self.parameters_frame, text=self._t("agent_parameters"), padding=10)
        agent_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        agents = ["generator_agent", "reviewer_agent", "remover_agent", "optimizer_agent"]
        self.agent_params = {}
        
        for i, agent in enumerate(agents):
            frame = ttk.LabelFrame(agent_frame, text=self._t(agent), padding=5)
            frame.grid(row=i//2, column=i%2, sticky='nsew', padx=5, pady=5)
            
            temp_var = tk.StringVar(value="0.7")
            tokens_var = tk.StringVar(value="150")
            
            tk.Label(frame, text=self._t("temperature")).grid(row=0, column=0, sticky='w', padx=3)
            tk.Entry(frame, textvariable=temp_var, width=10).grid(row=0, column=1, sticky='w', padx=3)
            
            tk.Label(frame, text=self._t("max_tokens")).grid(row=1, column=0, sticky='w', padx=3)
            tk.Entry(frame, textvariable=tokens_var, width=10).grid(row=1, column=1, sticky='w', padx=3)
            
            self.agent_params[agent] = {
                'temperature': temp_var,
                'max_tokens': tokens_var
            }
        
        agent_frame.columnconfigure(0, weight=1)
        agent_frame.columnconfigure(1, weight=1)
    
    def _create_evaluation_tab(self):
        """Create evaluation tab"""
        # Create main container with two columns
        main_container = tk.Frame(self.evaluation_frame)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left column - Controls and text output
        left_frame = tk.Frame(main_container)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Evaluation selection
        select_frame = ttk.LabelFrame(left_frame, text=self._t("evaluation_type"), padding=10)
        select_frame.pack(fill='x', padx=5, pady=5)
        
        # Hypergraph file (LLM Generated)
        tk.Label(select_frame, text=self._t("hypergraph_file"), font=("Arial", 10)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.eval_file_var = tk.StringVar()
        tk.Entry(select_frame, textvariable=self.eval_file_var, width=40).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        tk.Button(select_frame, text=self._t("browse"), command=lambda: self._browse_file(self.eval_file_var, False)).grid(row=0, column=2, padx=5, pady=5)
        
        # Real hypergraph file (for comparison)
        tk.Label(select_frame, text=self._t("real_hypergraph_file"), font=("Arial", 10)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.real_file_var = tk.StringVar()
        tk.Entry(select_frame, textvariable=self.real_file_var, width=40).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        tk.Button(select_frame, text=self._t("browse"), command=lambda: self._browse_file(self.real_file_var, False)).grid(row=1, column=2, padx=5, pady=5)
        
        # JS Divergence Comparison Button
        tk.Button(
            select_frame,
            text=self._t("js_divergence_comparison"),
            command=self._run_js_comparison,
            width=30,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold")
        ).grid(row=2, column=0, columnspan=3, padx=5, pady=15)
        
        # Evaluation buttons - Python evaluations
        python_frame = ttk.LabelFrame(select_frame, text="Python Evaluations", padding=5)
        python_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky='ew')
        
        python_eval_types = [
            ("basic_statistics", self._run_basic_stats),
            ("structural_counts", self._run_structural_counts),
            ("clustering_coefficient", self._run_clustering),
            ("spectral_similarity", self._run_spectral),
            ("motif_analysis", self._run_motif),
            ("community_detection_clique", self._run_community_clique)
        ]
        
        for i, (key, callback) in enumerate(python_eval_types):
            btn = tk.Button(
                python_frame,
                text=self._t(key),
                command=callback,
                width=25,
                height=2,
                bg="#2196F3",
                fg="white"
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        
        # MATLAB evaluations
        matlab_frame = ttk.LabelFrame(select_frame, text="MATLAB Evaluations", padding=5)
        matlab_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky='ew')
        
        # MATLAB "Run All" button
        tk.Button(
            matlab_frame,
            text=self._t("matlab_all_evaluations"),
            command=self._run_matlab_all,
            width=25,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        
        # Individual MATLAB evaluation buttons
        matlab_eval_types = [
            ("matlab_degrees", "degrees"),
            ("matlab_group_degrees", "group_degrees"),
            ("matlab_hyperedge_sizes", "hyperedge_sizes"),
            ("matlab_intersecting_pairs", "intersecting_pairs"),
            ("matlab_intersection_sizes", "intersection_sizes"),
            ("matlab_power_law", "power_law"),
            ("matlab_singular_values", "singular_values"),
            ("matlab_temporal_locality", "temporal_locality")
        ]
        
        for i, (key, eval_type) in enumerate(matlab_eval_types):
            btn = tk.Button(
                matlab_frame,
                text=self._t(key),
                command=lambda et=eval_type: self._run_matlab_specific(et),
                width=25,
                height=1,
                bg="#FFA726",
                fg="white"
            )
            btn.grid(row=(i//3)+1, column=i%3, padx=5, pady=3)
        
        # Results display
        results_frame = ttk.LabelFrame(left_frame, text=self._t("evaluation_results"), padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Right column - PDF Viewer
        right_frame = tk.Frame(main_container, width=500)
        right_frame.pack(side='right', fill='both', expand=False, padx=5)
        right_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        pdf_viewer_frame = ttk.LabelFrame(right_frame, text=self._t("pdf_viewer"), padding=10)
        pdf_viewer_frame.pack(fill='both', expand=True)
        
        # Chart selector buttons (1-8)
        selector_frame = tk.Frame(pdf_viewer_frame)
        selector_frame.pack(fill='x', pady=5)
        
        tk.Label(selector_frame, text=self._t("select_chart"), font=("Arial", 10, "bold")).pack(side='left', padx=5)
        
        self.pdf_files = []  # Store list of generated PDF files
        self.current_pdf_index = 0
        
        # Create 8 chart selection buttons
        button_container = tk.Frame(selector_frame)
        button_container.pack(side='left', padx=10)
        
        self.chart_buttons = []
        for i in range(8):
            btn = tk.Button(
                button_container,
                text=str(i+1),
                command=lambda idx=i: self._show_pdf_by_index(idx),
                width=3,
                height=1,
                bg="#E0E0E0",
                state='disabled'
            )
            btn.pack(side='left', padx=2)
            self.chart_buttons.append(btn)
        
        # Refresh button
        tk.Button(
            selector_frame,
            text="🔄",
            command=self._refresh_pdf_list,
            width=3,
            height=1
        ).pack(side='left', padx=5)
        
        # PDF display canvas
        canvas_frame = tk.Frame(pdf_viewer_frame, bg='white', relief='sunken', bd=2)
        canvas_frame.pack(fill='both', expand=True, pady=5)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white')
        self.pdf_canvas.pack(fill='both', expand=True)
        
        # Status label
        self.pdf_status_label = tk.Label(
            pdf_viewer_frame,
            text=self._t("no_pdf_generated"),
            font=("Arial", 9),
            fg="gray"
        )
        self.pdf_status_label.pack(pady=5)
        
        # Store current PDF image reference
        self.current_pdf_image = None
        
        self.eval_text = scrolledtext.ScrolledText(results_frame, height=20, wrap='word')
        self.eval_text.pack(fill='both', expand=True)
    
    def _create_entity_tab(self):
        """Create entity generation tab"""
        # Create main container with two columns
        main_container = tk.Frame(self.entity_frame)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left column - Generation controls
        left_frame = tk.Frame(main_container)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Generation method
        method_frame = ttk.LabelFrame(left_frame, text=self._t("generation_method"), padding=10)
        method_frame.pack(fill='x', padx=5, pady=5)
        
        self.entity_method_var = tk.StringVar(value="statistical")
        
        tk.Radiobutton(
            method_frame,
            text=self._t("statistical_generation"),
            variable=self.entity_method_var,
            value="statistical",
            font=("Arial", 10),
            command=self._on_method_change
        ).pack(anchor='w', padx=20, pady=5)
        
        tk.Radiobutton(
            method_frame,
            text=self._t("llm_generation"),
            variable=self.entity_method_var,
            value="llm",
            font=("Arial", 10),
            command=self._on_method_change
        ).pack(anchor='w', padx=20, pady=5)
        
        # Network type selector (for LLM generation)
        self.network_type_frame = ttk.LabelFrame(left_frame, text=self._t("network_type"), padding=10)
        self.network_type_frame.pack(fill='x', padx=5, pady=5)
        
        self.network_type_var = tk.StringVar(value="social")
        
        network_types = [
            ("social", self._t("network_social")),
            ("drug", self._t("network_drug")),
            ("research", self._t("network_research")),
            ("ecommerce", self._t("network_ecommerce"))
        ]
        
        for value, label in network_types:
            tk.Radiobutton(
                self.network_type_frame,
                text=label,
                variable=self.network_type_var,
                value=value,
                font=("Arial", 10)
            ).pack(anchor='w', padx=20, pady=3)
        
        # Initially hide network type selector
        self.network_type_frame.pack_forget()
        
        # Parameters
        param_frame = ttk.LabelFrame(left_frame, text=self._t("tab_parameters"), padding=10)
        param_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(param_frame, text=self._t("num_personas"), font=("Arial", 10)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.num_personas_var = tk.StringVar(value="1000")
        tk.Entry(param_frame, textvariable=self.num_personas_var, width=15).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        tk.Label(param_frame, text=self._t("output_file"), font=("Arial", 10)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entity_output_var = tk.StringVar(value="personas.json")
        tk.Entry(param_frame, textvariable=self.entity_output_var, width=30).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        tk.Button(param_frame, text=self._t("browse"), command=lambda: self._browse_file(self.entity_output_var, False, save=True)).grid(row=1, column=2, padx=5, pady=5)
        
        # Generate button
        tk.Button(
            param_frame,
            text=self._t("generate_personas"),
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self._generate_entities,
            height=2
        ).grid(row=2, column=0, columnspan=3, pady=20, sticky='ew', padx=50)
        
        # Log
        log_frame = ttk.LabelFrame(left_frame, text="Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.entity_log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap='word')
        self.entity_log_text.pack(fill='both', expand=True)
        
        # Right column - Personas Viewer
        right_frame = tk.Frame(main_container, width=400)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        viewer_frame = ttk.LabelFrame(right_frame, text=self._t("personas_viewer"), padding=10)
        viewer_frame.pack(fill='both', expand=True)
        
        # Personas file loader
        load_frame = tk.Frame(viewer_frame)
        load_frame.pack(fill='x', pady=5)
        
        self.viewer_file_var = tk.StringVar()
        tk.Entry(load_frame, textvariable=self.viewer_file_var, width=25).pack(side='left', padx=5)
        tk.Button(
            load_frame,
            text=self._t("browse"),
            command=lambda: self._browse_personas_for_viewer()
        ).pack(side='left', padx=5)
        tk.Button(
            load_frame,
            text=self._t("load_personas"),
            command=self._load_personas_viewer,
            bg="#4CAF50",
            fg="white"
        ).pack(side='left', padx=5)
        
        # Stats display
        stats_frame = tk.Frame(viewer_frame)
        stats_frame.pack(fill='x', pady=5)
        
        tk.Label(stats_frame, text=self._t("total_personas"), font=("Arial", 10, "bold")).pack(side='left', padx=5)
        self.total_personas_label = tk.Label(stats_frame, text="0", font=("Arial", 10))
        self.total_personas_label.pack(side='left', padx=5)
        
        # Search frame
        search_frame = tk.Frame(viewer_frame)
        search_frame.pack(fill='x', pady=5)
        
        tk.Label(search_frame, text=self._t("search_persona"), font=("Arial", 10)).pack(side='left', padx=5)
        self.search_persona_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_persona_var, width=15)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<Return>', lambda e: self._search_persona())
        tk.Button(
            search_frame,
            text="🔍",
            command=self._search_persona
        ).pack(side='left', padx=2)
        tk.Button(
            search_frame,
            text=self._t("refresh"),
            command=self._refresh_personas_list
        ).pack(side='left', padx=2)
        
        # Personas list with scrollbar
        list_frame = tk.Frame(viewer_frame)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.personas_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            height=15
        )
        self.personas_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.personas_listbox.yview)
        self.personas_listbox.bind('<<ListboxSelect>>', self._on_persona_select)
        
        # Details display
        details_frame = ttk.LabelFrame(viewer_frame, text=self._t("persona_details"), padding=5)
        details_frame.pack(fill='both', expand=True, pady=5)
        
        self.persona_details_text = scrolledtext.ScrolledText(
            details_frame,
            height=8,
            wrap='word',
            font=("Arial", 9)
        )
        self.persona_details_text.pack(fill='both', expand=True)
        
        # Store loaded personas data
        self.loaded_personas = {}
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Label(
            self.root,
            text=self._t("ready"),
            bd=1,
            relief='sunken',
            anchor='w'
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def _browse_file(self, var, is_directory=False, save=False):
        """Browse for file or directory"""
        if is_directory:
            path = filedialog.askdirectory()
        elif save:
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        else:
            path = filedialog.askopenfilename()
        
        if path:
            var.set(path)
    
    def _start_generation(self):
        """Start hypergraph generation"""
        # Validate inputs
        if not self.file_vars['config_file'].get():
            messagebox.showerror("Error", "Please select config file")
            return
        
        if not self.file_vars['personas_file'].get():
            messagebox.showerror("Error", "Please select personas file")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_bar.config(text=self._t("running"))
        
        # Start generation in separate thread
        self.generation_thread = threading.Thread(target=self._run_generation)
        self.generation_thread.daemon = True
        self.generation_thread.start()
    
    def _stop_generation(self):
        """Stop hypergraph generation"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_bar.config(text=self._t("ready"))
        self._log_message("Generation stopped by user")
    
    def _run_generation(self):
        """Run generation process"""
        try:
            # Ensure API configuration is set
            if self.api_base_url_var.get():
                os.environ['OPENAI_BASE_URL'] = self.api_base_url_var.get()
            
            # Build command
            script_path = Path(__file__).parent.parent / "Hypergraph-Generator" / "LLM_MAS_Hypergraph_Configuration.py"
            
            cmd = [
                sys.executable,
                str(script_path),
                "--personas", self.file_vars['personas_file'].get(),
                "--config", self.file_vars['config_file'].get(),
                "--output", "generated_hypergraph.txt",
                "--iterations", self.param_vars['iterations'].get(),
                "--groups_per_iter", self.param_vars['groups_per_iteration'].get(),
                "--max_members", self.param_vars['max_members'].get(),
                "--model", self.model_var.get(),
                "--preferential_attachment_prob", self.param_vars['preferential_attachment'].get()
            ]
            
            if self.file_vars['resume_directory'].get():
                cmd.extend(["--resume", self.file_vars['resume_directory'].get()])
            
            self._log_message(f"Starting generation: {' '.join(cmd)}")
            
            # Set UTF-8 environment for subprocess on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # Run process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace encoding errors instead of failing
                bufsize=1,
                env=env
            )
            
            # Read output
            for line in process.stdout:
                if not self.is_running:
                    process.terminate()
                    break
                
                self._log_message(line.strip())
                self._parse_output_line(line)
            
            process.wait()
            
            if self.is_running:
                self._log_message("Generation completed!")
                self.status_bar.config(text=self._t("completed"))
            
        except Exception as e:
            self._log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_running = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
    
    def _parse_output_line(self, line):
        """Parse output line and update UI"""
        try:
            # Detect phase
            if "Building Phase" in line or "建设阶段" in line:
                self.root.after(0, lambda: self.phase_label.config(text=self._t("building_phase"), fg="orange"))
            elif "Evolution Phase" in line or "演化阶段" in line:
                self.root.after(0, lambda: self.phase_label.config(text=self._t("evolution_phase"), fg="green"))
            
            # Detect hyperedge additions
            if "Added hyperedge" in line or "添加超边" in line or "✅" in line:
                self.root.after(0, lambda: self._add_hyperedge_display(line))
            
            # Update progress
            if "progress:" in line.lower() or "进度" in line:
                # Try to extract percentage
                import re
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    percent = float(match.group(1))
                    self.root.after(0, lambda p=percent: self.progress_bar.config(value=p))
        
        except Exception as e:
            pass  # Silently ignore parsing errors
    
    def _add_hyperedge_display(self, line):
        """Add hyperedge to display"""
        self.edges_text.insert('1.0', line + '\n')
        # Keep only last 100 lines
        lines = self.edges_text.get('1.0', 'end').split('\n')
        if len(lines) > 100:
            self.edges_text.delete(f'{len(lines) - 100}.0', 'end')
        
        # Update count
        current = self.edges_label.cget('text')
        try:
            count = int(current) + 1
            self.edges_label.config(text=str(count))
        except:
            pass
    
    def _log_message(self, message):
        """Add message to log"""
        if self.log_text:
            self.root.after(0, lambda: self.log_text.insert('end', message + '\n'))
            self.root.after(0, lambda: self.log_text.see('end'))
    
    # Evaluation methods
    def _run_basic_stats(self):
        """Run basic statistics"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        # Use visualization module for basic stats
        try:
            from visualization import HypergraphStats
            stats = HypergraphStats(self.eval_file_var.get())
            result_text = stats.format_stats_text()
            self.eval_text.delete('1.0', 'end')
            self.eval_text.insert('end', result_text)
        except Exception as e:
            self.eval_text.insert('end', f"\nError: {str(e)}\n")
            messagebox.showerror("Error", str(e))
    
    def _run_structural_counts(self):
        """Run structural counts"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        self._run_evaluation_script("hypergraph_structural_counts.py", [self.eval_file_var.get()])
    
    def _run_clustering(self):
        """Run clustering coefficient"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        self._run_evaluation_script("hypergraph_clustering_coefficient.py", [self.eval_file_var.get()])
    
    def _run_spectral(self):
        """Run spectral similarity"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        self._run_evaluation_script("hypergraph_spectral_similarity.py", [self.eval_file_var.get()])
    
    def _run_motif(self):
        """Run motif analysis"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        self._run_evaluation_script("hypergraph_motif_analysis.py", [self.eval_file_var.get()])
    
    def _run_community_clique(self):
        """Run community detection with clique expansion + Louvain"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        # Open community viewer window immediately
        viewer = CommunityViewerWindow(self.root, self.eval_file_var.get(), self.current_language, self._t)
        viewer.grab_set()  # Make window modal
    
    def _run_matlab_all(self):
        """Run all MATLAB evaluations using unified run_all_analysis.m"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        self.eval_text.insert('end', self._t("running_evaluation") + " (Unified Mode)\n\n")
        # Use all-unified mode with pdf format
        self._run_evaluation_script("matlab_evaluations_wrapper.py", [self.eval_file_var.get(), "all-unified", "pdf"])
        # Refresh PDF list after evaluation
        self.root.after(1000, self._refresh_pdf_list)
    
    def _run_matlab_specific(self, eval_type: str):
        """Run specific MATLAB evaluation"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", "Please select hypergraph file")
            return
        
        self.eval_text.insert('end', f"{self._t('running_evaluation')} ({eval_type})\n\n")
        self._run_evaluation_script("matlab_evaluations_wrapper.py", [self.eval_file_var.get(), eval_type])
        # Refresh PDF list after evaluation
        self.root.after(1000, self._refresh_pdf_list)
    
    def _run_evaluation_script(self, script_name, args):
        """Run evaluation script"""
        try:
            script_path = Path(__file__).parent.parent / "Hypergraph-Evaluation" / script_name
            
            # Build command with script path and arguments
            cmd = [sys.executable, str(script_path)] + args
            
            self.eval_text.insert('end', f"Running: {' '.join(cmd)}\n\n")
            
            # Set UTF-8 environment for subprocess on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace',  # Replace encoding errors instead of failing
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            self.eval_text.insert('end', result.stdout)
            if result.stderr:
                self.eval_text.insert('end', f"\nErrors:\n{result.stderr}")
            
            self.eval_text.see('end')
            
        except subprocess.TimeoutExpired:
            self.eval_text.insert('end', "\n⚠️ Evaluation timeout (5 minutes). Try with a smaller dataset.\n")
        except Exception as e:
            self.eval_text.insert('end', f"\nError: {str(e)}\n")
            messagebox.showerror("Error", str(e))
    
    def _run_js_comparison(self):
        """Run JS divergence comparison between LLM-generated and real hypergraphs"""
        if not self.eval_file_var.get():
            messagebox.showerror("Error", self._t("please_select_llm_file"))
            return
        
        if not self.real_file_var.get():
            messagebox.showerror("Error", self._t("please_select_real_file"))
            return
        
        self.eval_text.delete('1.0', 'end')
        self.eval_text.insert('end', f"{self._t('js_divergence_comparison')} 🎯\n")
        self.eval_text.insert('end', "="*60 + "\n\n")
        self.eval_text.insert('end', f"LLM-generated: {os.path.basename(self.eval_file_var.get())}\n")
        self.eval_text.insert('end', f"Real hypergraph: {os.path.basename(self.real_file_var.get())}\n\n")
        self.eval_text.insert('end', self._t("computing") + "...\n\n")
        self.eval_text.see('end')
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._run_js_comparison_thread, daemon=True)
        thread.start()
    
    def _run_js_comparison_thread(self):
        """Thread function for JS divergence comparison"""
        try:
            script_path = Path(__file__).parent.parent / "Hypergraph-Evaluation" / "hypergraph_distribution_analysis.py"
            
            # Generate output file names
            llm_file = self.eval_file_var.get()
            real_file = self.real_file_var.get()
            
            output_dir = Path(__file__).parent.parent / "Hypergraph-Evaluation" / "comparison_results"
            output_dir.mkdir(exist_ok=True)
            
            timestamp = os.path.basename(llm_file).replace('.txt', '')
            comparison_output = output_dir / f"comparison_{timestamp}.json"
            
            cmd = [
                sys.executable,
                str(script_path),
                llm_file,
                "--name", "LLM-Generated",
                "--real_file", real_file,
                "--real_name", "Real",
                "--comparison_output", str(comparison_output)
            ]
            
            self.root.after(0, lambda: self.eval_text.insert('end', f"Running: {' '.join([str(c) for c in cmd])}\n\n"))
            
            # Set UTF-8 environment for subprocess
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=1800  # 30 minute timeout for large datasets
            )
            
            # Display results
            self.root.after(0, lambda: self._display_comparison_results(result, comparison_output))
            
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.eval_text.insert('end', "\n⚠️ Computation timeout. Try with smaller datasets.\n"))
        except Exception as e:
            self.root.after(0, lambda: self.eval_text.insert('end', f"\n❌ Error: {str(e)}\n"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def _display_comparison_results(self, result, comparison_output):
        """Display comparison results in eval text widget"""
        # Display stdout
        self.eval_text.insert('end', result.stdout)
        
        if result.stderr:
            self.eval_text.insert('end', f"\nStderr:\n{result.stderr}\n")
        
        # Load and display JSON results
        if os.path.exists(comparison_output):
            try:
                with open(comparison_output, 'r') as f:
                    comparison = json.load(f)
                
                self.eval_text.insert('end', "\n" + "="*60 + "\n")
                self.eval_text.insert('end', "📊 JS DIVERGENCE COMPARISON SUMMARY\n")
                self.eval_text.insert('end', "="*60 + "\n\n")
                
                if 'overall' in comparison:
                    overall = comparison['overall']
                    if 'mean_js_divergence' in overall:
                        self.eval_text.insert('end', f"Overall Mean JS Divergence: {overall['mean_js_divergence']:.4f}\n")
                        self.eval_text.insert('end', f"Overall Median JS Divergence: {overall['median_js_divergence']:.4f}\n")
                        self.eval_text.insert('end', f"JS Range: [{overall['min_js_divergence']:.4f}, {overall['max_js_divergence']:.4f}]\n")
                    if 'mean_wasserstein' in overall:
                        self.eval_text.insert('end', f"Overall Mean Wasserstein Distance: {overall['mean_wasserstein']:.4f}\n")
                        self.eval_text.insert('end', f"Overall Median Wasserstein Distance: {overall['median_wasserstein']:.4f}\n")
                    if 'mean_ks_statistic' in overall:
                        self.eval_text.insert('end', f"Overall Mean KS Statistic: {overall['mean_ks_statistic']:.4f}\n")
                    self.eval_text.insert('end', "\n")
                
                # Display individual metrics
                self.eval_text.insert('end', "Individual Metrics:\n")
                self.eval_text.insert('end', "-" * 60 + "\n")
                
                for key, value in comparison.items():
                    if key != 'overall' and isinstance(value, dict):
                        self.eval_text.insert('end', f"\n{key}:\n")
                        
                        # JS Divergence
                        if 'js_divergence' in value:
                            js_div = value['js_divergence']
                            self.eval_text.insert('end', f"  JS Divergence: {js_div if isinstance(js_div, str) else f'{js_div:.4f}'}\n")
                        
                        # Wasserstein Distance
                        if 'wasserstein_distance' in value:
                            wd = value['wasserstein_distance']
                            self.eval_text.insert('end', f"  Wasserstein Distance: {wd:.4f}\n")
                        
                        # KS Statistic
                        if 'ks_statistic' in value and value['ks_statistic'] is not None:
                            ks = value['ks_statistic']
                            ks_p = value.get('ks_pvalue', 'N/A')
                            if isinstance(ks_p, (int, float)):
                                self.eval_text.insert('end', f"  KS Statistic: {ks:.4f} (p={ks_p:.4f})\n")
                            else:
                                self.eval_text.insert('end', f"  KS Statistic: {ks:.4f}\n")
                        
                        # L2 Distance (for singular values)
                        if 'l2_distance' in value:
                            l2 = value['l2_distance']
                            self.eval_text.insert('end', f"  L2 Distance: {l2:.4f}\n")
                        
                        # Power-law parameters
                        if 'self_powerlaw' in value and value['self_powerlaw'].get('success'):
                            gamma = value['self_powerlaw']['gamma']
                            self.eval_text.insert('end', f"  LLM γ: {gamma:.3f}\n")
                        
                        if 'other_powerlaw' in value and value['other_powerlaw'].get('success'):
                            gamma = value['other_powerlaw']['gamma']
                            self.eval_text.insert('end', f"  Real γ: {gamma:.3f}\n")
                        
                        # Note if not power-law
                        if 'self_powerlaw' in value and not value['self_powerlaw'].get('success'):
                            reason = value['self_powerlaw'].get('reason', 'Unknown')
                            self.eval_text.insert('end', f"  Note: {reason}\n")
                
                self.eval_text.insert('end', "\n" + "="*60 + "\n")
                self.eval_text.insert('end', f"✅ Results saved to: {comparison_output}\n")
                
            except Exception as e:
                self.eval_text.insert('end', f"\n❌ Error parsing results: {str(e)}\n")
        
        self.eval_text.see('end')
    
    def _on_method_change(self):
        """Handle generation method change"""
        method = self.entity_method_var.get()
        if method == "llm":
            # Show network type selector
            self.network_type_frame.pack(fill='x', padx=5, pady=5)
        else:
            # Hide network type selector
            self.network_type_frame.pack_forget()
    
    def _generate_entities(self):
        """Generate entity personas"""
        try:
            method = self.entity_method_var.get()
            num_personas = int(self.num_personas_var.get())
            output_file = self.entity_output_var.get()
            
            if method == "statistical":
                # Use generate_personas.py for US demographics-based generation
                script_name = "generate_personas.py"
                script_path = Path(__file__).parent.parent / "Hypergraph-Entity" / script_name
                cmd = [sys.executable, str(script_path), str(num_personas), output_file]
            else:
                # Use entity_generator.py for LLM-based generation
                script_name = "entity_generator.py"
                script_path = Path(__file__).parent.parent / "Hypergraph-Entity" / script_name
                network_type = self.network_type_var.get()
                
                cmd = [
                    sys.executable, str(script_path),
                    "--entity_type", network_type,
                    "--n", str(num_personas),
                    "--output", output_file
                ]
                
                # Add API config if available
                if hasattr(self, 'api_key_var') and self.api_key_var.get():
                    # Save API key to temp file
                    api_key_file = Path(__file__).parent.parent / "temp_api_key.txt"
                    with open(api_key_file, 'w') as f:
                        f.write(self.api_key_var.get())
                    cmd.extend(["--api_key_file", str(api_key_file)])
                
                if hasattr(self, 'api_base_url_var') and self.api_base_url_var.get():
                    cmd.extend(["--base_url", self.api_base_url_var.get()])
            
            self.entity_log_text.insert('end', f"Running: {' '.join(cmd)}\n\n")
            
            # Set UTF-8 environment for subprocess on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace encoding errors instead of failing
                bufsize=1,
                env=env
            )
            
            for line in process.stdout:
                self.entity_log_text.insert('end', line)
                self.entity_log_text.see('end')
                self.root.update()
            
            process.wait()
            
            self.entity_log_text.insert('end', "\nGeneration completed!\n")
            messagebox.showinfo("Success", f"Generated {num_personas} entities to {output_file}")
            
        except Exception as e:
            self.entity_log_text.insert('end', f"\nError: {str(e)}\n")
            messagebox.showerror("Error", str(e))


    def _save_api_config(self):
        """Save API configuration to file"""
        try:
            api_key = self.api_key_var.get()
            api_base_url = self.api_base_url_var.get()
            
            if not api_key or not api_base_url:
                messagebox.showwarning("Warning", "Please enter both API key and base URL")
                return
            
            # Save to environment and config file
            config_dir = Path(__file__).parent.parent / "Hypergraph-Generator"
            api_key_file = config_dir / "api-key.txt"
            
            # Save API key
            with open(api_key_file, 'w') as f:
                f.write(api_key)
            
            # Set environment variable for current session
            os.environ['OPENAI_BASE_URL'] = api_base_url
            
            # Save to GUI config for next session
            gui_config_file = Path(__file__).parent / "api_config.json"
            with open(gui_config_file, 'w') as f:
                json.dump({
                    'api_base_url': api_base_url
                }, f)
            
            messagebox.showinfo("Success", self._t("api_config_saved"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API config: {str(e)}")
    
    def _load_api_config(self):
        """Load existing API configuration"""
        try:
            # Load API key
            config_dir = Path(__file__).parent.parent / "Hypergraph-Generator"
            api_key_file = config_dir / "api-key.txt"
            
            if api_key_file.exists():
                with open(api_key_file, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        self.api_key_var.set(api_key)
            
            # Load base URL from environment or config
            base_url = os.environ.get('OPENAI_BASE_URL', '')
            if not base_url:
                gui_config_file = Path(__file__).parent / "api_config.json"
                if gui_config_file.exists():
                    with open(gui_config_file, 'r') as f:
                        config = json.load(f)
                        base_url = config.get('api_base_url', '')
            
            if base_url:
                self.api_base_url_var.set(base_url)
                os.environ['OPENAI_BASE_URL'] = base_url
                
        except Exception as e:
            print(f"Error loading API config: {e}")
    
    def _browse_personas_for_viewer(self):
        """Browse for personas file for viewer"""
        path = filedialog.askopenfilename(
            title="Select Personas File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.viewer_file_var.set(path)
    
    def _load_personas_viewer(self):
        """Load personas file into viewer"""
        file_path = self.viewer_file_var.get()
        
        if not file_path:
            messagebox.showwarning("Warning", self._t("load_file_first"))
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.loaded_personas = json.load(f)
            
            # Update total count
            self.total_personas_label.config(text=str(len(self.loaded_personas)))
            
            # Populate listbox
            self._refresh_personas_list()
            
            messagebox.showinfo("Success", f"Loaded {len(self.loaded_personas)} personas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load personas: {str(e)}")
    
    def _refresh_personas_list(self):
        """Refresh personas list display"""
        if not self.loaded_personas:
            return
        
        # Clear listbox
        self.personas_listbox.delete(0, tk.END)
        
        # Add all personas
        for persona_id in sorted(self.loaded_personas.keys(), key=lambda x: int(x) if x.isdigit() else x):
            persona = self.loaded_personas[persona_id]
            # Format: ID | Gender | Race | Age
            display_text = f"{persona_id:>5} | {persona.get('gender', 'N/A'):<8} | {persona.get('race/ethnicity', 'N/A'):<20} | Age {persona.get('age', 'N/A')}"
            self.personas_listbox.insert(tk.END, display_text)
    
    def _search_persona(self):
        """Search for specific persona by ID"""
        if not self.loaded_personas:
            messagebox.showwarning("Warning", self._t("load_file_first"))
            return
        
        search_id = self.search_persona_var.get().strip()
        
        if not search_id:
            self._refresh_personas_list()
            return
        
        # Clear and populate with matching results
        self.personas_listbox.delete(0, tk.END)
        
        found = False
        for persona_id in sorted(self.loaded_personas.keys()):
            if search_id.lower() in persona_id.lower():
                persona = self.loaded_personas[persona_id]
                display_text = f"{persona_id:>5} | {persona.get('gender', 'N/A'):<8} | {persona.get('race/ethnicity', 'N/A'):<20} | Age {persona.get('age', 'N/A')}"
                self.personas_listbox.insert(tk.END, display_text)
                found = True
        
        if not found:
            self.personas_listbox.insert(tk.END, f"No personas found matching '{search_id}'")
    
    def _on_persona_select(self, event):
        """Handle persona selection in listbox"""
        if not self.personas_listbox.curselection():
            return
        
        # Get selected item
        index = self.personas_listbox.curselection()[0]
        selected_text = self.personas_listbox.get(index)
        
        # Extract persona ID (first part before |)
        persona_id = selected_text.split('|')[0].strip()
        
        if persona_id in self.loaded_personas:
            persona = self.loaded_personas[persona_id]
            
            # Format details
            details = f"=== Persona ID: {persona_id} ===\n\n"
            for key, value in persona.items():
                details += f"{key.title()}: {value}\n"
            
            # Display in details panel
            self.persona_details_text.delete('1.0', 'end')
            self.persona_details_text.insert('1.0', details)


    # PDF Viewer methods
    def _refresh_pdf_list(self):
        """Refresh list of generated PDF files from plots directory"""
        try:
            plots_dir = Path(__file__).parent.parent / "Hypergraph-Evaluation" / "plots"
            
            if not plots_dir.exists():
                self.pdf_status_label.config(text=self._t("no_pdf_generated"))
                return
            
            # Find all PDF files in plots directory
            pdf_files = sorted(glob.glob(str(plots_dir / "*.pdf")))
            self.pdf_files = pdf_files
            
            # Enable/disable buttons based on available files
            for i, btn in enumerate(self.chart_buttons):
                if i < len(pdf_files):
                    btn.config(state='normal', bg="#4CAF50")
                else:
                    btn.config(state='disabled', bg="#E0E0E0")
            
            if pdf_files:
                self.pdf_status_label.config(
                    text=f"{len(pdf_files)} PDF(s) found",
                    fg="green"
                )
                # Automatically display the first PDF
                self._show_pdf_by_index(0)
            else:
                self.pdf_status_label.config(
                    text=self._t("no_pdf_generated"),
                    fg="gray"
                )
                
        except Exception as e:
            print(f"Error refreshing PDF list: {e}")
    
    def _show_pdf_by_index(self, index):
        """Show PDF by index"""
        if index >= len(self.pdf_files):
            return
        
        pdf_path = self.pdf_files[index]
        self.current_pdf_index = index
        
        # Highlight selected button
        for i, btn in enumerate(self.chart_buttons):
            if i == index:
                btn.config(bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
            elif i < len(self.pdf_files):
                btn.config(bg="#4CAF50", fg="black", font=("Arial", 9))
        
        # Display PDF
        self._display_pdf(pdf_path)
    
    def _display_pdf(self, pdf_path):
        """Display PDF file as image"""
        try:
            # Try to use pdf2image library
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
                if images:
                    img = images[0]
                else:
                    raise Exception("No pages in PDF")
            except ImportError:
                # Fallback: Display a message if pdf2image is not installed
                self._display_pdf_unavailable_message()
                return
            
            # Resize image to fit canvas
            canvas_width = self.pdf_canvas.winfo_width()
            canvas_height = self.pdf_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 480
            if canvas_height <= 1:
                canvas_height = 600
            
            # Calculate scaling factor
            img_width, img_height = img.size
            scale_w = (canvas_width - 20) / img_width
            scale_h = (canvas_height - 20) / img_height
            scale = min(scale_w, scale_h, 1.0)  # Don't upscale
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img_resized)
            
            # Clear canvas
            self.pdf_canvas.delete("all")
            
            # Display image
            x = canvas_width // 2
            y = canvas_height // 2
            self.pdf_canvas.create_image(x, y, image=photo, anchor='center')
            
            # Keep reference to prevent garbage collection
            self.current_pdf_image = photo
            
            # Update status
            pdf_name = Path(pdf_path).name
            self.pdf_status_label.config(
                text=f"📄 {pdf_name}",
                fg="blue"
            )
            
        except Exception as e:
            self.pdf_status_label.config(
                text=f"Error: {str(e)}",
                fg="red"
            )
            print(f"Error displaying PDF: {e}")
    
    def _display_pdf_unavailable_message(self):
        """Display message when pdf2image is not available"""
        self.pdf_canvas.delete("all")
        
        canvas_width = self.pdf_canvas.winfo_width()
        canvas_height = self.pdf_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 480
        if canvas_height <= 1:
            canvas_height = 600
        
        x = canvas_width // 2
        y = canvas_height // 2
        
        message = "PDF Viewer requires 'pdf2image' library\n\n"
        message += "Install with:\n"
        message += "pip install pdf2image\n\n"
        message += "PDFs are saved in:\n"
        message += "Hypergraph-Evaluation/plots/"
        
        self.pdf_canvas.create_text(
            x, y,
            text=message,
            font=("Arial", 12),
            fill="gray",
            justify='center'
        )
        
        self.pdf_status_label.config(
            text="pdf2image library not installed",
            fg="orange"
        )


class CommunityViewerWindow(tk.Toplevel):
    """Window for viewing community detection results and node details"""
    
    def __init__(self, parent, hypergraph_file: str, language: str, translate_func):
        super().__init__(parent)
        
        self.hypergraph_file = hypergraph_file
        self.language = language
        self._t = translate_func
        
        # Data storage
        self.community_data = None
        self.personas_data = None
        
        # Setup window
        self.title(self._t("community_viewer"))
        self.geometry("1400x800")
        
        # Create UI
        self._create_ui()
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_ui(self):
        """Create user interface"""
        # Main container
        main_container = tk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top: Run community detection
        run_frame = ttk.LabelFrame(main_container, text=self._t("run_community_detection"), padding=10)
        run_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(run_frame, text=self._t("hypergraph_file") + f": {Path(self.hypergraph_file).name}", font=("Arial", 10)).pack(side='left', padx=5)
        
        tk.Button(
            run_frame,
            text=self._t("run_detection"),
            command=self._run_detection,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2
        ).pack(side='right', padx=5)
        
        # Status label
        self.status_label = tk.Label(run_frame, text=self._t("ready"), font=("Arial", 10), fg="blue")
        self.status_label.pack(side='right', padx=20)
        
        # Info panel - shows after detection
        self.info_frame = ttk.LabelFrame(main_container, text=self._t("community_summary"), padding=10)
        
        self.info_text = tk.Label(self.info_frame, text="", font=("Arial", 11, "bold"), justify='left')
        self.info_text.pack()
        
        # Personas file loader
        self.personas_frame = ttk.LabelFrame(main_container, text=self._t("load_personas_file"), padding=10)
        
        tk.Label(self.personas_frame, text=self._t("personas_file"), font=("Arial", 10)).pack(side='left', padx=5)
        self.personas_file_var = tk.StringVar()
        tk.Entry(self.personas_frame, textvariable=self.personas_file_var, width=50).pack(side='left', padx=5)
        tk.Button(
            self.personas_frame,
            text=self._t("browse"),
            command=self._browse_personas_file
        ).pack(side='left', padx=5)
        tk.Button(
            self.personas_frame,
            text=self._t("load_personas"),
            command=self._load_personas,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side='left', padx=5)
        
        # Split container
        self.split_container = tk.Frame(main_container)
        
        # Left panel - Community list
        left_frame = ttk.LabelFrame(self.split_container, text=self._t("community_list"), padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Search frame
        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill='x', pady=5)
        
        tk.Label(search_frame, text=self._t("search_community"), font=("Arial", 10)).pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._filter_communities())
        
        # Community listbox
        listbox_frame = tk.Frame(left_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.community_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            height=20
        )
        self.community_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.community_listbox.yview)
        
        self.community_listbox.bind('<<ListboxSelect>>', self._on_community_select)
        
        # Right panel - Node details
        right_frame = ttk.LabelFrame(self.split_container, text=self._t("community_nodes"), padding=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Nodes in community
        nodes_frame = tk.Frame(right_frame)
        nodes_frame.pack(fill='both', expand=True)
        
        # Node listbox
        nodes_listbox_frame = tk.Frame(nodes_frame)
        nodes_listbox_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(nodes_listbox_frame, text=self._t("nodes_in_community"), font=("Arial", 10, "bold")).pack(anchor='w')
        
        nodes_scrollbar = tk.Scrollbar(nodes_listbox_frame)
        nodes_scrollbar.pack(side='right', fill='y')
        
        self.nodes_listbox = tk.Listbox(
            nodes_listbox_frame,
            yscrollcommand=nodes_scrollbar.set,
            font=("Courier", 10),
            height=25
        )
        self.nodes_listbox.pack(side='left', fill='both', expand=True)
        nodes_scrollbar.config(command=self.nodes_listbox.yview)
        
        self.nodes_listbox.bind('<<ListboxSelect>>', self._on_node_select)
        
        # Node details panel
        details_frame = tk.Frame(nodes_frame)
        details_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        tk.Label(details_frame, text=self._t("node_details"), font=("Arial", 10, "bold")).pack(anchor='w')
        
        self.node_details_text = scrolledtext.ScrolledText(
            details_frame,
            width=50,
            height=25,
            wrap='word',
            font=("Courier", 9)
        )
        self.node_details_text.pack(fill='both', expand=True)
    
    def _run_detection(self):
        """Run community detection in background thread"""
        self.status_label.config(text=self._t("running") + "...", fg="orange")
        thread = threading.Thread(target=self._run_detection_thread, daemon=True)
        thread.start()
    
    def _run_detection_thread(self):
        """Background thread for running detection"""
        try:
            script_path = Path(__file__).parent.parent / "Hypergraph-Evaluation" / "hypergraph_community_detection.py"
            
            # Generate output filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(__file__).parent.parent / "Hypergraph-Evaluation" / "community_results" / f"communities_{timestamp}.json"
            output_file.parent.mkdir(exist_ok=True)
            
            cmd = [sys.executable, str(script_path), self.hypergraph_file, str(output_file)]
            
            # Set UTF-8 environment
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=900  # Increased to 15 minutes for large hypergraphs
            )
            
            if result.returncode == 0 and output_file.exists():
                # Load results
                self.after(0, lambda: self._load_detection_results(str(output_file)))
            else:
                self.after(0, lambda: messagebox.showerror("Error", f"Detection failed:\n{result.stderr}"))
                self.after(0, lambda: self.status_label.config(text=self._t("ready"), fg="blue"))
            
        except subprocess.TimeoutExpired:
            self.after(0, lambda: messagebox.showerror("Error", "Detection timeout (15 minutes). Try with a smaller hypergraph or use command line for large datasets."))
            self.after(0, lambda: self.status_label.config(text=self._t("ready"), fg="blue"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.status_label.config(text=self._t("ready"), fg="blue"))
    
    def _load_detection_results(self, json_file: str):
        """Load detection results from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.community_data = json.load(f)
            
            # Update UI
            self.status_label.config(text=self._t("completed"), fg="green")
            
            # Show info panel
            self.info_frame.pack(fill='x', padx=5, pady=5)
            
            # Display summary statistics
            num_communities = self.community_data.get('num_communities', 0)
            modularity = self.community_data.get('modularity', 0)
            avg_size = self.community_data.get('avg_community_size', 0)
            max_size = self.community_data.get('max_community_size', 0)
            min_size = self.community_data.get('min_community_size', 0)
            
            stats_text = f"Communities: {num_communities}  |  "
            stats_text += f"Modularity Q: {modularity:.4f}  |  "
            stats_text += f"Avg Size: {avg_size:.1f}  |  "
            stats_text += f"Range: [{min_size}, {max_size}]"
            
            self.info_text.config(text=stats_text)
            
            # Show personas loader and split container
            if not self.personas_frame.winfo_ismapped():
                self.personas_frame.pack(fill='x', padx=5, pady=5)
            if not self.split_container.winfo_ismapped():
                self.split_container.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Populate community list
            self._populate_community_list()
            
            messagebox.showinfo("Success", f"Detected {num_communities} communities!\nModularity Q = {modularity:.4f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results: {str(e)}")
            self.status_label.config(text=self._t("ready"), fg="blue")
    
    def _browse_personas_file(self):
        """Browse for personas JSON file"""
        filename = filedialog.askopenfilename(
            title=self._t("select_personas_file"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.personas_file_var.set(filename)
    
    def _load_personas(self):
        """Load personas data from file"""
        file_path = self.personas_file_var.get()
        
        if not file_path:
            messagebox.showwarning("Warning", self._t("please_select_personas_file"))
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.personas_data = json.load(f)
            
            messagebox.showinfo("Success", f"{self._t('loaded')} {len(self.personas_data)} {self._t('personas')}")
            
            # Refresh current community display if one is selected
            if self.community_listbox.curselection():
                self._on_community_select(None)
                
        except Exception as e:
            messagebox.showerror("Error", f"{self._t('failed_to_load')}: {str(e)}")
    
    def _populate_community_list(self):
        """Populate community list"""
        if not self.community_data:
            return
        
        self.community_listbox.delete(0, tk.END)
        
        community_sizes = self.community_data.get('community_sizes', {})
        
        # Sort by size (descending)
        sorted_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)
        
        for comm_id, size in sorted_communities:
            display_text = f"Community {comm_id:3s}:  {size:4d} nodes  {'█' * min(30, size // 5)}"
            self.community_listbox.insert(tk.END, display_text)
    
    def _filter_communities(self):
        """Filter communities by search term"""
        if not self.community_data:
            return
        
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self._populate_community_list()
            return
        
        self.community_listbox.delete(0, tk.END)
        
        community_sizes = self.community_data.get('community_sizes', {})
        sorted_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)
        
        for comm_id, size in sorted_communities:
            if search_term in str(comm_id).lower():
                display_text = f"Community {comm_id:3s}:  {size:4d} nodes  {'█' * min(30, size // 5)}"
                self.community_listbox.insert(tk.END, display_text)
    
    def _on_community_select(self, event):
        """Handle community selection"""
        if not self.community_listbox.curselection() or not self.community_data:
            return
        
        # Get selected community ID
        index = self.community_listbox.curselection()[0]
        selected_text = self.community_listbox.get(index)
        
        # Extract community ID
        comm_id = selected_text.split(':')[0].replace('Community', '').strip()
        
        # Get nodes in this community
        node_communities = self.community_data.get('node_communities', {})
        nodes_in_community = [node for node, comm in node_communities.items() if str(comm) == comm_id]
        
        # Sort nodes
        try:
            nodes_in_community = sorted(nodes_in_community, key=lambda x: int(x) if x.isdigit() else x)
        except:
            nodes_in_community = sorted(nodes_in_community)
        
        # Display nodes
        self.nodes_listbox.delete(0, tk.END)
        
        for node_id in nodes_in_community:
            if self.personas_data and node_id in self.personas_data:
                persona = self.personas_data[node_id]
                display_text = f"{node_id:>5} | {persona.get('gender', 'N/A'):<8} | {persona.get('race/ethnicity', 'N/A'):<15}"
            else:
                display_text = f"{node_id:>5} | (No persona data loaded)"
            
            self.nodes_listbox.insert(tk.END, display_text)
        
        # Clear node details
        self.node_details_text.delete('1.0', tk.END)
        self.node_details_text.insert('1.0', f"Community {comm_id} - {len(nodes_in_community)} nodes\n\n")
        self.node_details_text.insert('end', f"Select a node to view details...")
    
    def _on_node_select(self, event):
        """Handle node selection"""
        if not self.nodes_listbox.curselection():
            return
        
        # Get selected node ID
        index = self.nodes_listbox.curselection()[0]
        selected_text = self.nodes_listbox.get(index)
        
        # Extract node ID
        node_id = selected_text.split('|')[0].strip()
        
        # Display node details
        self.node_details_text.delete('1.0', tk.END)
        
        if not self.personas_data:
            self.node_details_text.insert('1.0', f"Node ID: {node_id}\n\n")
            self.node_details_text.insert('end', f"(No persona data loaded)\n\n")
            self.node_details_text.insert('end', f"Please load personas JSON file to view details.")
            return
        
        if node_id in self.personas_data:
            persona = self.personas_data[node_id]
            
            # Format details
            details = f"{'='*50}\n"
            details += f"  NODE ID: {node_id}\n"
            details += f"{'='*50}\n\n"
            
            for key, value in persona.items():
                details += f"{key.upper()}:\n"
                details += f"  {value}\n\n"
            
            self.node_details_text.insert('1.0', details)
        else:
            self.node_details_text.insert('1.0', f"Node ID: {node_id}\n\n")
            self.node_details_text.insert('end', f"(Not found in personas data)")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = HyperLLMGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

