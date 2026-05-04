class Themes:
    # Minimalist selectors that target internal content panels
    DARK = """
    /* Main Panel Backgrounds */
    QWidget#BrowsePanel, QWidget#DownloadPanel, QWidget#SettingsPanel, QFrame#headerFrame, QWidget#tabBrowse, QWidget#tabDownload, QWidget#tabSettings { 
        background-color: #0b0b19; 
        color: #eaeaf4;
    }
    
    QTabWidget::pane { border: none; background-color: #0b0b19; }
    QTabBar::tab { background-color: #13132c; color: #9494b4; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
    QTabBar::tab:selected { background-color: #e94560; color: #ffffff; }
    
    QLabel, QCheckBox, QGroupBox { color: #eaeaf4; background: transparent; }
    QLineEdit, QComboBox, QSpinBox { background-color: #181836; border: 1px solid #242444; border-radius: 4px; padding: 6px; color: #eaeaf4; }
    
    /* ScrollBar */
    QScrollBar:vertical { background: #0b0b19; width: 10px; margin: 0px; }
    QScrollBar::handle:vertical { background: #242444; min-height: 20px; border-radius: 5px; }
    QScrollBar::handle:vertical:hover { background: #e94560; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """

    LIGHT = """
    /* Main Panel Backgrounds */
    QWidget#BrowsePanel, QWidget#DownloadPanel, QWidget#SettingsPanel, QFrame#headerFrame, QWidget#tabBrowse, QWidget#tabDownload, QWidget#tabSettings { 
        background-color: #f8fafc; 
        color: #1e293b;
    }

    QTabWidget::pane { border: none; background-color: #f8fafc; }
    QTabBar::tab { background-color: #f1f5f9; color: #64748b; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
    QTabBar::tab:selected { background-color: #3b82f6; color: #ffffff; }
    
    QLabel, QCheckBox, QGroupBox { color: #1e293b; background: transparent; }
    QLineEdit, QComboBox, QSpinBox { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; color: #1e293b; }

    /* ScrollBar */
    QScrollBar:vertical { background: #f8fafc; width: 10px; margin: 0px; }
    QScrollBar::handle:vertical { background: #cbd5e1; min-height: 20px; border-radius: 5px; }
    QScrollBar::handle:vertical:hover { background: #3b82f6; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """
