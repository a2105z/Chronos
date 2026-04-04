/** Single task row with delete action. */

import type { Task } from "../../types/task";
import { buildTaskMetaLine } from "./formatTaskMeta";

interface TaskRowProps {
  task: Task;
  onDelete: (taskId: number) => void;
  onEdit: (task: Task) => void;
}

export function TaskRow({ task, onDelete, onEdit }: TaskRowProps) {
  function handleDeleteClick() {
    onDelete(task.id);
  }

  const metaLine = buildTaskMetaLine(task);

  function handleEditClick() {
    onEdit(task);
  }

  return (
    <li className="task-item">
      <div>
        <strong>{task.name}</strong>
        <span className="task-meta">{metaLine}</span>
      </div>
      <div className="task-row-actions">
        <button className="btn-secondary btn-compact" type="button" onClick={handleEditClick}>
          Edit
        </button>
        <button
          className="btn-danger btn-compact"
          type="button"
          onClick={handleDeleteClick}
          aria-label="Delete task"
        >
          Delete
        </button>
      </div>
    </li>
  );
}
