import { DndContext } from "@dnd-kit/core";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import BoardColumn from "../../src/frontend/src/components/BoardColumn";
import type { BoardColumn as ColumnType, Task } from "../../src/frontend/src/api/types";

const column: ColumnType = {
  status: "in_progress",
  title: "В работе",
  position: 2,
  wip_limit: 3,
};

function makeTask(id: number): Task {
  return {
    id,
    board_id: 1,
    title: `Задача ${id}`,
    description: "",
    status: "in_progress",
    priority: "medium",
    position: id,
    author_id: 1,
    assignee_id: null,
    branch: null,
    estimate_hours: null,
    created_at: "2026-10-28T10:00:00Z",
    updated_at: "2026-10-28T10:00:00Z",
    assignee: null,
  };
}

function renderColumn(tasks: Task[]) {
  render(
    <DndContext>
      <BoardColumn
        column={column}
        tasks={tasks}
        canDelete={false}
        onDelete={vi.fn()}
        onAdd={vi.fn()}
      />
    </DndContext>,
  );
}

describe("Колонка доски", () => {
  it("показывает заголовок, счётчик задач и лимит", () => {
    renderColumn([makeTask(1), makeTask(2)]);
    expect(screen.getByText("В работе")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("лимит 3")).toBeInTheDocument();
  });

  it("подсказывает, что колонка пуста", () => {
    renderColumn([]);
    expect(screen.getByText("Перетащите карточку сюда")).toBeInTheDocument();
  });

  it("выделяет лимит, когда он достигнут", () => {
    renderColumn([makeTask(1), makeTask(2), makeTask(3)]);
    expect(screen.getByText("лимит 3").className).toContain("text-red-600");
  });
});
