import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import type { BoardColumn as ColumnType, Task } from "../api/types";
import TaskCard from "./TaskCard";

interface Props {
  column: ColumnType;
  tasks: Task[];
  canDelete: boolean;
  onDelete: (task: Task) => void;
  onAdd: (status: string) => void;
}

export default function BoardColumn({ column, tasks, canDelete, onDelete, onAdd }: Props) {
  const { setNodeRef, isOver } = useDroppable({ id: column.status });
  const overLimit = column.wip_limit != null && tasks.length >= column.wip_limit;

  return (
    <div className="flex flex-col w-72 shrink-0">
      <div className="flex items-center justify-between px-1 mb-2">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-700">{column.title}</h2>
          <span className="text-xs text-slate-400">{tasks.length}</span>
          {column.wip_limit != null && (
            <span
              className={`text-[11px] px-1.5 py-0.5 rounded ${
                overLimit ? "bg-red-100 text-red-600" : "bg-slate-100 text-slate-500"
              }`}
              title="Ограничение на количество задач в колонке"
            >
              лимит {column.wip_limit}
            </span>
          )}
        </div>
        <button
          onClick={() => onAdd(column.status)}
          className="text-slate-400 hover:text-accent text-lg leading-none"
          aria-label={`Добавить задачу в колонку ${column.title}`}
        >
          +
        </button>
      </div>

      <div
        ref={setNodeRef}
        className={`flex-1 rounded-xl p-2 space-y-2 min-h-[120px] transition ${
          isOver ? "bg-blue-50 ring-2 ring-accent/30" : "bg-slate-200/40"
        }`}
      >
        <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} canDelete={canDelete} onDelete={onDelete} />
          ))}
        </SortableContext>

        {tasks.length === 0 && (
          <p className="text-xs text-slate-400 text-center py-6">Перетащите карточку сюда</p>
        )}
      </div>
    </div>
  );
}
