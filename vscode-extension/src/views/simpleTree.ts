import * as vscode from "vscode";
import { TreeRow } from "../types";

export class SimpleTreeProvider implements vscode.TreeDataProvider<TreeRow> {
  private rows: TreeRow[] = [];
  private readonly changed = new vscode.EventEmitter<TreeRow | undefined | null | void>();
  readonly onDidChangeTreeData = this.changed.event;

  setRows(rows: TreeRow[]): void {
    this.rows = rows;
    this.changed.fire();
  }

  getTreeItem(element: TreeRow): vscode.TreeItem {
    const item = new vscode.TreeItem(element.label, vscode.TreeItemCollapsibleState.None);
    item.description = element.description;
    item.tooltip = element.tooltip;
    item.command = element.command as vscode.Command | undefined;
    item.contextValue = element.contextValue;
    if (element.icon) {
      item.iconPath = new vscode.ThemeIcon(element.icon);
    }
    return item;
  }

  getChildren(): Thenable<TreeRow[]> {
    return Promise.resolve(this.rows);
  }
}
