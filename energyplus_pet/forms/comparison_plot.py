from enum import auto, Enum
import matplotlib
matplotlib.use('TkAgg')

# unfortunately, with newer flake8, you cannot tag the .use() line with noqa, you have to tag *every* trailing import
# I considered just ignoring E402 for this project, as the files are generally small anyway, but for now, noqa here

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
import numpy as np  # noqa: E402
from tkinter import Frame, Toplevel, TOP, BOTH, Tk  # noqa: E402
from tkinter.ttk import Notebook  # noqa: E402

from energyplus_pet.data_manager import CatalogDataManager  # noqa: E402
from energyplus_pet.equipment.base import BaseEquipment  # noqa: E402


class ComparisonPlot(Toplevel):

    class PlotType(Enum):
        RawComparison = auto()
        PercentError = auto()

    def __init__(self, parent_window: Tk, _: CatalogDataManager, equip_instance: BaseEquipment):
        super().__init__(parent_window)
        self.title(f"{parent_window.title()}: Results Comparison")
        data_per_type = {
            ComparisonPlot.PlotType.RawComparison: {
                "tab_title": "Catalog Data Raw Comparison",
                "plot_title": "Model vs. Catalog Data Points",
                "plot_data": equip_instance.get_absolute_plot_data(),
                "y_label": "[Data could be multiple units]"
            },
            ComparisonPlot.PlotType.PercentError: {
                "tab_title": "Percent Error Comparison",
                "plot_title": "Percent Error (hopefully near zero!)",
                "plot_data": equip_instance.get_error_plot_data(),
                "y_label": "Percent Error [%]"
            }
        }
        plot_notebook = Notebook(self)
        for plot_type in list(ComparisonPlot.PlotType):
            data_this_plot_type = data_per_type[plot_type]
            plot_frame = Frame(plot_notebook)
            plot_frame.pack(side=TOP, expand=True, fill=BOTH)
            plot_notebook.add(plot_frame, text=data_this_plot_type['tab_title'])
            fig = Figure()
            a = fig.add_subplot(111)
            plot_title = data_this_plot_type['plot_title']
            for pd in data_this_plot_type['plot_data']:
                if pd[1] == 'line':
                    line_arg = '-'
                elif pd[1] == 'point':
                    line_arg = '--'
                else:
                    raise Exception('bad line type')
                a.plot(np.array(pd[3]), label=pd[0], linestyle=line_arg, color=pd[2])
            a.legend()
            a.set_title(plot_title, fontsize=16)
            a.set_xlabel("Catalog Data Points (no order)")
            a.set_ylabel(data_this_plot_type['y_label'])
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.get_tk_widget().pack()
            canvas.draw()
        plot_notebook.pack(side=TOP, expand=True, fill=BOTH)
        self.grab_set()
        self.transient(parent_window)


if __name__ == "__main__":
    from tkinter import Tk
    from energyplus_pet.equipment.wahp_heating_curve import WaterToAirHeatPumpHeatingCurveFit
    window = Tk()
    cdm = CatalogDataManager()
    eq = WaterToAirHeatPumpHeatingCurveFit()
    eq.catalog_load_side_heating_capacity = [100.0, 200.0, 300.0]
    eq.predicted_load_side_heating_capacity = [100.00001, 200.00001, 299.99999]
    eq.percent_error_load_side_heating_capacity = [0.0000001, 0.00000001, 0.0000001]
    ComparisonPlot(window, cdm, eq)
    window.mainloop()
