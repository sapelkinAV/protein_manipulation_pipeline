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
                TextArea(id="plan_description"),
                
                Label("PDB ID (optional):"),
                Input(placeholder="e.g. 1ABC", id="pdb_id"),
                
                Label("Local PDB Path (optional):"),
                Input(placeholder="/path/to/file.pdb", id="local_pdb"),
                
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
        """Create new plan from form data."""
        name = self.query_one("#plan_name", Input).value.strip()
        description = self.query_one("#plan_description", TextArea).text.strip()
        pdb_id = self.query_one("#pdb_id", Input).value.strip()
        local_pdb = self.query_one("#local_pdb", Input).value.strip()
        
        if not name:
            self.notify("Plan name is required", severity="error")
            return
        
        plan = self.plan_manager.create_plan(
            name=name,
            description=description,
            pdb_id=pdb_id or None,
            local_pdb_path=local_pdb or None
        )
        
        # If PDB info provided, automatically add a PDB fetch step
        if pdb_id or local_pdb:
            from pathlib import Path
            
            pdb_config = {
                'pdb_id': pdb_id or name,
                'file_input_mode': 'searchPDB' if pdb_id else 'upload',
                'file_path': str(Path(local_pdb)) if local_pdb else None,
                'membrane_config': {
                    'membrane_type': 'custom',
                    'popc': True,
                    'dopc': False,
                    'dspc': False,
                    'dmpc': False,
                    'dppc': False,
                    'chol_value': 20.0,
                    'protein_topology': 'in'
                },
                'ion_configuration': {
                    'ion_concentration': 0.15,
                    'ion_type': 'KCl'
                }
            }
            
            self.plan_manager.add_pdb_fetch_step(
                plan_id=plan.id,
                name="Fetch PDB File",
                description="Download or load PDB file with specified configuration",
                pdb_config=pdb_config
            )
        
        self.notify(f"Plan '{name}' created successfully")
        self.app.pop_screen()


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
    }
    
    .buttons {
        height: 3;
        align: center middle;
    }
    
    .main_container, .form_container, .detail_container {
        margin: 2;
    }
    
    ListView {
        height: 1fr;
        border: solid $accent;
    }
    
    Input, TextArea {
        margin: 1 0;
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