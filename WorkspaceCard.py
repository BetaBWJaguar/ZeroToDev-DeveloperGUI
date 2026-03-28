# -*- coding: utf-8 -*-
from tkinter import ttk


class WorkspaceCard(ttk.Frame):

    def __init__(self, parent, workspace_data, on_click, on_archive=None, **kwargs):
        super().__init__(parent, style="WorkspaceCard.TFrame", **kwargs)
        self.workspace_data = workspace_data
        self.on_click = on_click
        self.on_archive = on_archive
        self.is_hovered = False
        
        self.grid_columnconfigure(1, weight=1)
        
        self._build_content()
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
        self._bind_children(self)
    
    def _bind_children(self, widget):
        for child in widget.winfo_children():
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)
            if not isinstance(child, ttk.Button):
                child.bind("<Button-1>", self._on_click)
            self._bind_children(child)
    
    def _build_content(self):
        icon_frame = ttk.Frame(self, style="WorkspaceIcon.TFrame")
        icon_frame.grid(row=0, column=0, sticky="ns", padx=(8, 4), pady=8)
        
        icon_label = ttk.Label(icon_frame, text="📁", font=("Segoe UI", 16))
        icon_label.pack()
        
        content_frame = ttk.Frame(self, style="WorkspaceContent.TFrame")
        content_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=8)
        
        name_label = ttk.Label(
            content_frame,
            text=self.workspace_data.get('name', 'N/A'),
            style="WorkspaceName.TLabel",
            font=("Segoe UI", 11, "bold")
        )
        name_label.pack(anchor="w")
        
        path_label = ttk.Label(
            content_frame,
            text=self.workspace_data.get('path', 'N/A'),
            style="WorkspacePath.TLabel",
            font=("Segoe UI", 9)
        )
        path_label.pack(anchor="w", pady=(2, 0))
        
        if self.workspace_data.get('description'):
            desc_label = ttk.Label(
                content_frame,
                text=self.workspace_data['description'],
                style="WorkspaceDesc.TLabel",
                font=("Segoe UI", 9),
                wraplength=300
            )
            desc_label.pack(anchor="w", pady=(4, 0))

        actions_frame = ttk.Frame(self, style="WorkspaceActions.TFrame")
        actions_frame.grid(row=0, column=2, sticky="ns", padx=(4, 8), pady=8)
        
        click_label = ttk.Label(
            actions_frame,
            text="→",
            style="WorkspaceClick.TLabel",
            width=2,
            anchor="center"
        )
        click_label.pack(side="left", padx=(0, 4))
        
        if self.on_archive:
            archive_btn = ttk.Button(
                actions_frame,
                text="📦",
                style="Accent.TButton",
                width=3
            )
            archive_btn.pack(side="left")
            archive_btn.bind("<Button-1>", lambda e: self._on_archive_click(e))

    def _on_enter(self, event):
        if not self.is_hovered:
            self.is_hovered = True
            self.configure(style="WorkspaceCardHover.TFrame")
            self.configure(cursor="hand2")
            self._update_children_style("hover")

    def _on_leave(self, event):
        self.after(10, self._check_leave, event)

    def _check_leave(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)

        if widget is None or not self._is_child_of(widget):
            if self.is_hovered:
                self.is_hovered = False
                self.configure(style="WorkspaceCard.TFrame")
                self._update_children_style("normal")

    
    def _on_click(self, event):
        self.on_click(self.workspace_data.get('workspace_id'))
    
    def _on_archive_click(self, event):
        if self.on_archive:
            self.on_archive(self.workspace_data.get('workspace_id'))
        return "break"
    
    def _is_child_of(self, widget):
        parent = widget
        while parent:
            if parent == self:
                return True
            parent = parent.master
        return False

    def _update_children_style(self, state):
        style_map = {
            "WorkspaceName.TLabel": "WorkspaceName.TLabelHover",
            "WorkspacePath.TLabel": "WorkspacePath.TLabelHover",
            "WorkspaceDesc.TLabel": "WorkspaceDesc.TLabelHover",
            "WorkspaceClick.TLabel": "WorkspaceClick.TLabelHover",
            "WorkspaceContent.TFrame": "WorkspaceContentHover.TFrame",
            "WorkspaceIcon.TFrame": "WorkspaceIconHover.TFrame",
        }

        for widget in self.winfo_children():
            if isinstance(widget, ttk.Label):
                current_style = widget.cget('style')

                if widget.cget("text") in ("→", "➜"):
                    if state == "hover":
                        widget.configure(text="➜")
                    else:
                        widget.configure(text="→")

                if state == "hover" and current_style in style_map:
                    widget.configure(style=style_map[current_style])

                elif state == "normal" and current_style in style_map.values():
                    for normal_style, hover_style in style_map.items():
                        if current_style == hover_style:
                            widget.configure(style=normal_style)
                            break

            self._update_child_style_recursive(widget, state, style_map)
    
    def _update_child_style_recursive(self, widget, state, style_map):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Label):
                current_style = child.cget('style')
                if state == "hover" and current_style in style_map:
                    child.configure(style=style_map[current_style])
                elif state == "normal" and current_style in style_map.values():
                    for normal_style, hover_style in style_map.items():
                        if current_style == hover_style:
                            child.configure(style=normal_style)
                            break
            self._update_child_style_recursive(child, state, style_map)
