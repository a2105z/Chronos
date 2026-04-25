import { useState } from "react";
import { updateTask } from "../../api/client";
import type { PreferredTimeOfDay, Task, TaskCreate } from "../../types/task";
import { isoToDateInput, toIsoDateFromInput } from "../../utils/dates";
import "./TaskEditDialog.css";
import type { ReactElement } from "react";

interface TaskEditDialogProps {
  task: Task;
  onClose: () => void;
  onSaved: () => void;
}

export function TaskEditDialog({ task, onClose, onSaved }: TaskEditDialogProps) {
  const [name, setName] = useState(task.name);
  const [estimatedMinutes, setEstimatedMinutes] = useState(task.estimated_duration_minutes);
  const [priority, setPriority] = useState(task.priority);
  const [splittable, setSplittable] = useState(task.splittable);
  const [preferred, setPreferred] = useState<PreferredTimeOfDay>(
    (task.preferred_time_of_day as PreferredTimeOfDay) || "anytime"
  );
  const [earliestStart, setEarliestStart] = useState(isoToDateInput(task.earliest_start));
  const [deadline, setDeadline] = useState(isoToDateInput(task.deadline));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (name.trim() === "") {
      return;
    }
    setSaving(true);
    setError(null);
    let payload: Partial<TaskCreate> = {
      name: name.trim(),
      estimated_duration_minutes: estimatedMinutes,
      priority,
      splittable,
      preferred_time_of_day: preferred,
      earliest_start: toIsoDateFromInput(earliestStart),
      deadline: toIsoDateFromInput(deadline)
    };
    try {
      await updateTask(task.id, payload);
      onSaved();
      onClose();
    } catch {
      setError("Could not save changes.");
    } finally {
      setSaving(false);
    }
  }

  let errorBanner: ReactElement | null = null;
  if (error !== null) {
    errorBanner = <p className="form-error-banner">{error}</p>;
  }

  let saveButtonText = "Save";
  if (saving) {
    saveButtonText = "Saving…";
  }

  return (
    <div className="task-edit-overlay" role="dialog" aria-modal="true" aria-labelledby="task-edit-title">
      <div className="task-edit-dialog">
        <div className="task-edit-header">
          <h3 id="task-edit-title">Edit task</h3>
          <button type="button" className="btn-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        <form className="task-edit-form" onSubmit={handleSubmit}>
          {errorBanner}
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            Estimated minutes
            <input
              type="number"
              min={1}
              value={estimatedMinutes}
              onChange={(e) => setEstimatedMinutes(parseInt(e.target.value, 10) || 1)}
            />
          </label>
          <label>
            Priority
            <input
              type="number"
              min={0}
              value={priority}
              onChange={(e) => setPriority(parseInt(e.target.value, 10) || 0)}
            />
          </label>
          <label>
            Preferred time
            <select value={preferred} onChange={(e) => setPreferred(e.target.value as PreferredTimeOfDay)}>
              <option value="anytime">Anytime</option>
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
              <option value="evening">Evening</option>
            </select>
          </label>
          <label>
            <input type="checkbox" checked={splittable} onChange={(e) => setSplittable(e.target.checked)} />
            Splittable
          </label>
          <label>
            Earliest start (optional)
            <input type="date" value={earliestStart} onChange={(e) => setEarliestStart(e.target.value)} />
          </label>
          <label>
            Deadline (optional)
            <input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
          </label>
          <div className="task-edit-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saveButtonText}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
