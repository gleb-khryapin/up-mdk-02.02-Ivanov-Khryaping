import { DndContext } from "@dnd-kit/core";
import { SortableContext } from "@dnd-kit/sortable";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import TaskCard from "../../src/frontend/src/components/TaskCard";
import type { Task } from "../../src/frontend/src/api/types";

const task: Task = {
  id: 7,
  board_id: 1,
  title: "Реализовать вход по JWT",
  description: "Форма входа и хранение токена",
  status: "in_progress",
  priority: "high",
  position: 0,
  author_id: 1,
  assignee_id: 2,
  branch: "feature/auth-jwt",
  estimate_hours: 4,
  created_at: "2026-10-28T10:00:00Z",
  updated_at: "2026-10-28T10:00:00Z",
  assignee: { id: 2, email: "dev@teamboard.ru", full_name: "Иванов В. В.", role: "developer" },
};

function renderCard(props: Partial<React.ComponentProps<typeof TaskCard>> = {}) {
  const onDelete = props.onDelete ?? vi.fn();
  render(
    <DndContext>
      <SortableContext items={[task.id]}>
        <TaskCard task={task} canDelete={props.canDelete ?? false} onDelete={onDelete} />
      </SortableContext>
    </DndContext>,
  );
  return { onDelete };
}

describe("Карточка задачи", () => {
  it("показывает название, исполнителя и ветку", () => {
    renderCard();
    expect(screen.getByText("Реализовать вход по JWT")).toBeInTheDocument();
    expect(screen.getByText("Иванов В. В.")).toBeInTheDocument();
    expect(screen.getByText("feature/auth-jwt")).toBeInTheDocument();
  });

  it("отображает приоритет на русском языке", () => {
    renderCard();
    expect(screen.getByText("высокий")).toBeInTheDocument();
  });

  it("скрывает кнопку удаления от разработчика", () => {
    renderCard({ canDelete: false });
    expect(screen.queryByLabelText("Удалить задачу")).not.toBeInTheDocument();
  });

  it("показывает кнопку удаления тимлиду и передаёт задачу обработчику", async () => {
    const { onDelete } = renderCard({ canDelete: true });
    const button = screen.getByLabelText("Удалить задачу");
    await userEvent.click(button);
    expect(onDelete).toHaveBeenCalledWith(task);
  });
});
