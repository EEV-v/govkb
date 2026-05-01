export class CommandRunState {
  private readonly active = new Set<string>();

  isRunning(key: string): boolean {
    return this.active.has(key);
  }

  start(key: string): boolean {
    if (this.active.has(key)) {
      return false;
    }
    this.active.add(key);
    return true;
  }

  finish(key: string): void {
    this.active.delete(key);
  }

  async run<T>(key: string, task: () => Promise<T>): Promise<{ started: boolean; value?: T }> {
    if (!this.start(key)) {
      return { started: false };
    }
    try {
      return { started: true, value: await task() };
    } finally {
      this.finish(key);
    }
  }
}
