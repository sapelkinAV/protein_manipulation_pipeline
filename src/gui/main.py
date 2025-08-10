from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, ListView, ListItem, Label, Input, TextArea
from textual.screen import Screen
from textual.binding import Binding
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.plan_manager import PlanManager
from core.models import AnalysisPlan, AnalysisStep, StepStatus


class PlanListScreen(Screen):
    """Main screen showing list of analysis plans."""
    
    def __init__(self):
        super().__init__()
        self.plan_manager = PlanManager()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Analysis Plans", classes="title"),
                ListView(
                    id="plans_list"
                ),
                Horizontal(
                    Button("New Plan", id="new_plan", variant="success"),
                    Button("Refresh", id="refresh", variant="primary"),
                    Button("Exit", id="exit", variant="error"),
                    classes="buttons"
                ),
                classes="main_container"
            )
        )
        yield Footer()
    
    def on_mount(self):
        self.load_plans()
    
    def load_plans(self):
        """Load and display plans."""
        plans_list = self.query_one("#plans_list", ListView)
        plans_list.clear()
        
        plans = self.plan_manager.list_plans()
        for plan in plans:
            item_text = f"{plan.name} ({plan.id}) - {plan.status.value}"
            if plan.pdb_id:
                item_text += f" - PDB: {plan.pdb_id}"
            
            item = ListItem(Label(item_text))
            item.plan_id = plan.id
            plans_list.append(item)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new_plan":
            self.app.push_screen(NewPlanScreen())
        elif event.button.id == "refresh":
            self.load_plans()
        elif event.button.id == "exit":
            self.app.exit()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if hasattr(event.item, 'plan_id'):
            self.app.plan_id = event.item.plan_id
            self.app.push_screen(PlanDetailScreen())


class NewPlanScreen(Screen):
    """Screen for creating new analysis plans."""
    
    def __init__(self):
        super().__init__()
        self.plan_manager = PlanManager()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Create New Analysis Plan", classes="title"),
                
                Label("Plan Name:"),
                Input(placeholder="Enter plan name", id="plan_name"),
                
                Label("Description:"),
                TextArea(id="plan_description", classes="small_textarea"),
                
                Label("PDB Configuration", classes="section_title"),
                
                Label("PDB ID:"),
                Input(placeholder="e.g. 1ABC", id="pdb_id"),
                
                Label("Local PDB Path:"),
                Input(placeholder="/path/to/file.pdb", id="local_pdb"),
                
                Label("Membrane Type:"),
                Input(placeholder="e.g. PMm, custom", id="membrane_type"),
                
                Label("Cholesterol %:"),
                Input(placeholder="20.0", id="chol_value"),
                
                Label("Ion Type:"),
                Input(placeholder="KCl, NaCl", id="ion_type"),
                
                Label("Ion Concentration (M):"),
                Input(placeholder="0.15", id="ion_concentration"),
                
                Label("Temperature (K):"),
                Input(placeholder="303.15", id="temperature"),
                
                Label("Water Thickness (Å):"),
                Input(placeholder="22.5", id="water_thickness"),
                
                Horizontal(
                    Button("Create", id="create", variant="success"),
                    Button("Cancel", id="cancel", variant="error"),
                    classes="buttons"
                ),
                classes="form_container"
            )
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.create_plan()
        elif event.button.id == "cancel":
            self.app.pop_screen()
    
    def create_plan(self):
        """Create new plan from form data with PDB configuration."""
        name = self.query_one("#plan_name", Input).value.strip()
        description = self.query_one("#plan_description", TextArea).text.strip()
        pdb_id = self.query_one("#pdb_id", Input).value.strip()
        local_pdb = self.query_one("#local_pdb", Input).value.strip()
        membrane_type = self.query_one("#membrane_type", Input).value.strip() or "custom"
        chol_value = self.query_one("#chol_value", Input).value.strip() or "20.0"
        ion_type = self.query_one("#ion_type", Input).value.strip() or "KCl"
        ion_concentration = self.query_one("#ion_concentration", Input).value.strip() or "0.15"
        temperature = self.query_one("#temperature", Input).value.strip() or "303.15"
        water_thickness = self.query_one("#water_thickness", Input).value.strip() or "22.5"
        
        if not name:
            self.notify("Plan name is required", severity="error")
            return
        
        plan = self.plan_manager.create_plan(
            name=name,
            description=description,
            pdb_id=pdb_id or None,
            local_pdb_path=local_pdb or None
        )
        
        # Add PDB fetch step with configured parameters
        if pdb_id or local_pdb:
            from pathlib import Path
            
            try:
                chol_float = float(chol_value) if chol_value else 20.0
                ion_conc_float = float(ion_concentration) if ion_concentration else 0.15
                temp_float = float(temperature) if temperature else 303.15
                water_float = float(water_thickness) if water_thickness else 22.5
            except ValueError:
                self.notify("Invalid numeric values, using defaults", severity="warning")
                chol_float = 20.0
                ion_conc_float = 0.15
                temp_float = 303.15
                water_float = 22.5
            
            pdb_config = {
                'pdb_id': pdb_id or name,
                'file_input_mode': 'searchPDB' if pdb_id else 'upload',
                'file_path': str(Path(local_pdb)) if local_pdb else None,
                'membrane_config': {
                    'membrane_type': membrane_type,
                    'popc': True,
                    'dopc': False,
                    'dspc': False,
                    'dmpc': False,
                    'dppc': False,
                    'chol_value': chol_float,
                    'protein_topology': 'in'
                },
                'ion_configuration': {
                    'ion_concentration': ion_conc_float,
                    'ion_type': ion_type
                },
                'temperature': temp_float,
                'water_thickness_z': water_float,
                'perform_charmm_minimization': True
            }
            
            self.plan_manager.add_pdb_fetch_step(
                plan_id=plan.id,
                name="Fetch PDB File",
                description=f"Download/Load PDB {pdb_id or name} with membrane configuration",
                pdb_config=pdb_config
            )
        
        self.notify(f"Plan '{name}' created successfully")
        self.app.pop_screen()


class ConfigEditScreen(Screen):
    """Screen for editing step configurations."""
    
    def __init__(self):
        super().__init__()
        self.plan_manager = PlanManager()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Edit Step Configurations", classes="title"),
                
                Label("Select Step:"),
                ListView(
                    id="steps_config_list"
                ),
                
                Label("Configuration (YAML format):"),
                TextArea(id="config_editor", classes="config_editor"),
                
                Horizontal(
                    Button("Save", id="save_config", variant="success"),
                    Button("Cancel", id="cancel_config", variant="error"),
                    classes="buttons"
                ),
                classes="config_container"
            )
        )
        yield Footer()
    
    def on_mount(self):
        self.load_steps()
    
    def load_steps(self):
        """Load and display steps with configurations."""
        plan = self.plan_manager.get_plan(self.app.plan_id)
        if not plan:
            self.notify("Plan not found", severity="error")
            self.app.pop_screen()
            return
        
        steps_list = self.query_one("#steps_config_list", ListView)
        steps_list.clear()
        
        for i, step in enumerate(plan.steps):
            step_text = f"{i+1}. {step.name} - {step.step_type}"
            if step.configuration:
                step_text += " (has config)"
            
            item = ListItem(Label(step_text))
            item.step_index = i
            steps_list.append(item)
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Load selected step's configuration."""
        if hasattr(event.item, 'step_index'):
            plan = self.plan_manager.get_plan(self.app.plan_id)
            if plan and 0 <= event.item.step_index < len(plan.steps):
                step = plan.steps[event.item.step_index]
                config_editor = self.query_one("#config_editor", TextArea)
                
                import yaml
                if step.configuration:
                    config_editor.text = yaml.dump(step.configuration, default_flow_style=False)
                else:
                    config_editor.text = "# No configuration for this step\n{}"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_config":
            self.save_configuration()
        elif event.button.id == "cancel_config":
            self.app.pop_screen()
    
    def save_configuration(self):
        """Save the edited configuration."""
        try:
            selected = self.query_one("#steps_config_list", ListView).highlighted_child
            if not selected or not hasattr(selected, 'step_index'):
                self.notify("Please select a step first", severity="warning")
                return
            
            plan = self.plan_manager.get_plan(self.app.plan_id)
            if not plan:
                self.notify("Plan not found", severity="error")
                return
            
            step_index = selected.step_index
            if not (0 <= step_index < len(plan.steps)):
                self.notify("Invalid step selection", severity="error")
                return
            
            config_text = self.query_one("#config_editor", TextArea).text
            
            import yaml
            parsed_config = yaml.safe_load(config_text)
            
            if not isinstance(parsed_config, dict):
                self.notify("Configuration must be a valid YAML dictionary", severity="error")
                return
            
            plan.steps[step_index].configuration = parsed_config
            self.plan_manager._save_plan(plan)
            
            self.notify("Configuration saved successfully")
            self.load_steps()  # Refresh the list
            
        except yaml.YAMLError as e:
            self.notify(f"Invalid YAML format: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error saving configuration: {e}", severity="error")


class PlanDetailScreen(Screen):
    """Screen showing details of a specific plan."""
    
    def __init__(self):
        super().__init__()
        self.plan_manager = PlanManager()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Plan Details", classes="title", id="plan_title"),
                
                Label("", id="plan_info"),
                
                Label("Steps:", classes="section_title"),
                ListView(
                    id="steps_list"
                ),
                
                Horizontal(
                    Button("Add Step", id="add_step", variant="success"),
                    Button("Execute", id="execute", variant="primary"),
                    Button("View Config", id="view_config", variant="warning"),
                    Button("Back", id="back"),
                    classes="buttons"
                ),
                classes="detail_container"
            )
        )
        yield Footer()
    
    def on_mount(self):
        self.load_plan_details()
    
    def load_plan_details(self):
        """Load and display plan details."""
        plan = self.plan_manager.get_plan(self.app.plan_id)
        if not plan:
            self.notify("Plan not found", severity="error")
            self.app.pop_screen()
            return
        
        title = self.query_one("#plan_title", Label)
        title.update(f"Plan: {plan.name}")
        
        info = self.query_one("#plan_info", Label)
        info_text = f"ID: {plan.id}\n"
        info_text += f"Status: {plan.status.value}\n"
        info_text += f"Description: {plan.description}\n"
        if plan.pdb_id:
            info_text += f"PDB ID: {plan.pdb_id}\n"
        if plan.local_pdb_path:
            info_text += f"Local PDB: {plan.local_pdb_path}\n"
        # Show step configurations in the steps list
        if plan.steps:
            info_text += f"\nSteps: {len(plan.steps)} total\n"
        info.update(info_text)
        
        steps_list = self.query_one("#steps_list", ListView)
        steps_list.clear()
        
        for step in plan.steps:
            step_text = f"{step.order + 1}. {step.name} - {step.status.value}"
            item = ListItem(Label(step_text))
            steps_list.append(item)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "add_step":
            self.notify("Add step functionality not implemented yet")
        elif event.button.id == "execute":
            self.notify("Execute functionality not implemented yet")
        elif event.button.id == "view_config":
            self.app.push_screen(ConfigEditScreen())


class OprlmApp(App):
    """Main TUI application."""
    
    CSS = """
    .title {
        text-style: bold;
        text-align: center;
        margin: 1;
    }
    
    .section_title {
        text-style: bold;
        margin-top: 1;
        color: $accent;
    }
    
    .buttons {
        height: 3;
        align: center middle;
    }
    
    .main_container, .form_container, .detail_container {
        margin: 1;
    }
    
    .small_textarea {
        height: 3;
        margin: 1 0;
    }
    
    .config_editor {
        height: 15;
        border: solid $accent;
    }
    
    ListView {
        height: 1fr;
        border: solid $accent;
    }
    
    Input, TextArea {
        margin: 1 0;
    }
    
    #plan_description {
        height: 3;
    }
    
    .config_container {
        margin: 1;
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.plan_id = None
    
    def on_mount(self):
        self.push_screen(PlanListScreen())


if __name__ == "__main__":
    app = OprlmApp()
    app.run()