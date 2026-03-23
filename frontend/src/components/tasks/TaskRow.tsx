/** Single task row with delete action. */

import type { Task } from "../../types/task";
import { buildTaskMetaLine } from "./formatTaskMeta";

interface TaskRowProps {
  task: Task;
  onDelete: (taskId: number) => void;
}

export function TaskRow({ task, onDelete }: TaskRowProps) {
  function handleDeleteClick() {
    onDelete(task.id);
  }

  const metaLine = buildTaskMetaLine(task);

  return (
    <li className="task-item">
      <div>
        <strong>{task.name}</strong>
        <span className="task-meta">{metaLine}</span>
      </div>
      <button
        className="btn-danger"
        type="button"
        onClick={handleDeleteClick}
        aria-label="Delete task"
      >
        Delete
      </button>
    </li>
  );
}
