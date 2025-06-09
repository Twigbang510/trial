export class PriorityQueue {
  private nodes: [string, number][] = [];

  enqueue(id: string, priority: number): void {
    this.nodes.push([id, priority]);
    this.nodes.sort((a, b) => a[1] - b[1]);
  }

  dequeue(): [string, number] | undefined {
    return this.nodes.shift();
  }

  isEmpty(): boolean {
    return this.nodes.length === 0;
  }
}
