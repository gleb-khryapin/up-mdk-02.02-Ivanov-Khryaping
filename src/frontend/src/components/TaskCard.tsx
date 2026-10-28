import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { Task } from "../api/types";

const PRIORITY_STYLE: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
};

const PRIORITY_LABEL: Record<string, string> = {
  low: "низкий",
  medium: "средний",
  high: "высокий",
};

interface Props {
  task: Task;
  canDelete: boolean;
  onDelete: (task: Task) => void;
}

export default function TaskCard({ task, canDelete, onDelete }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-card rounded-lg border border-slate-200 p-3 shadow-sm hover:shadow transition group"
      data-testid={`task-${task.id}`}
    >
      <div className="flex items-start gap-2">
        <button
          {...attributes}
          {...listeners}
          className="cursor-grab text-slate-300 hover:text-slate-500 mt-0.5"
          aria-label="Переместить карточку"
        >
          ⠿
        </button>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium leading-snug">{task.title}</p>

          {task.description && (
            <p className="text-xs text-slate-500 mt-1 line-clamp-2">{task.description}</p>
          )}

          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            <span className={`text-[11px] px-1.5 py-0.5 rounded ${PRIORITY_STYLE[task.priority]}`}>
              {PRIORITY_LABEL[task.priority]}
            </span>
            {task.branch && (
              <span className="text-[11px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-600 font-mono">
                {task.branch}
              </span>
            )}
            {task.estimate_hours != null && (
              <span className="text-[11px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                {task.estimate_hours} ч
              </span>
            )}
          </div>

          <div className="flex items-center justify-between mt-2">
            <span className="text-[11px] text-slate-400">
              {task.assignee ? task.assignee.full_name : "не назначено"}
            </span>
            <span className="text-[11px] text-slate-300">#{task.id}</span>
          </div>
        </div>

        {canDelete && (
          <button
            onClick={() => onDelete(task)}
            className="opacity-0 group-hover:opacity-100 text-slate-300 hover:text-red-500 text-sm"
            aria-label="Удалить задачу"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
