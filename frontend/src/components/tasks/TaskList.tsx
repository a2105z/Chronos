/** Task list screen: load tasks, create new ones, delete existing. */

import { useState, useEffect } from "react";
import type { ReactNode } from "react";
import { getTasks, createTask, deleteTask } from "../../api/client";
import { toIsoDateFromInput } from "../../utils/dates";
import type { Task, TaskCreate } from "../../types/task";
import { DEFAULT_TASK_FORM } from "./taskFormDefaults";
import { TaskForm } from "./TaskForm";
import { TaskRow } from "./TaskRow";
import "./TaskList.css";

interface TaskListProps {
  onTaskCreated?: () => void;
}

function parseMinutesFromInput(raw: string, fallback: number): number {
  const parsed = parseInt(raw, 10);
  if (isNaN(parsed)) {
    return fallback;
  }
  return parsed;
}

function parseNonNegativeHours(raw: string): number {
  const parsed = parseInt(raw, 10);
  if (isNaN(parsed)) {
    return 0;
  }
  if (parsed < 0) {
    return 0;
  }
  return parsed;
}

function clampMinutesPart(raw: string): number {
  const parsed = parseInt(raw, 10);
  if (isNaN(parsed)) {
    return 0;
  }
  if (parsed < 0) {
    return 0;
  }
  if (parsed > 59) {
    return 59;
  }
  return parsed;
}

export default function TaskList({ onTaskCreated }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<TaskCreate>(DEFAULT_TASK_FORM);
  const [finishWindowStart, setFinishWindowStart] = useState("");
  const [finishWindowEnd, setFinishWindowEnd] = useState("");
  const [durationHours, setDurationHours] = useState(0);
  const [durationMinutesPart, setDurationMinutesPart] = useState(30);

  async function loadTasks() {
    try {
      const response = await getTasks();
      setTasks(response.data);
    } catch {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(function loadTasksOnMount() {
    loadTasks();
  }, []);

  function isFinishWindowInvalid(): boolean {
    if (finishWindowStart === "" || finishWindowEnd === "") {
      return false;
    }
    if (finishWindowEnd < finishWindowStart) {
      return true;
    }
    return false;
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    if (formData.name.trim() === "") {
      return;
    }
    if (isFinishWindowInvalid()) {
      return;
    }

    const earliestStart = toIsoDateFromInput(finishWindowStart);
    const deadline = toIsoDateFromInput(finishWindowEnd);

    try {
      await createTask({
        ...formData,
        earliest_start: earliestStart,
        deadline,
      });
      setFormData({ ...DEFAULT_TASK_FORM });
      setFinishWindowStart("");
      setFinishWindowEnd("");
      setDurationHours(0);
      setDurationMinutesPart(30);
      setShowForm(false);
      loadTasks();
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (err) {
      console.error("Failed to create task:", err);
    }
  }

  async function handleDelete(taskId: number) {
    try {
      await deleteTask(taskId);
      loadTasks();
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  }

  function handleToggleForm() {
    setShowForm(!showForm);
  }

  function handleNameChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFormData({ ...formData, name: event.target.value });
  }

  function handleDurationTotalChange(event: React.ChangeEvent<HTMLInputElement>) {
    const mins = parseMinutesFromInput(event.target.value, 30);
    setFormData({
      ...formData,
      estimated_duration_minutes: mins,
    });
    setDurationHours(Math.floor(mins / 60));
    setDurationMinutesPart(mins % 60);
  }

  function updateDurationFromParts(hours: number, minutesPart: number) {
    const totalMinutes = Math.max(1, hours * 60 + minutesPart);
    setFormData({
      ...formData,
      estimated_duration_minutes: totalMinutes,
    });
  }

  function handleDurationHoursChange(event: React.ChangeEvent<HTMLInputElement>) {
    const nextHours = parseNonNegativeHours(event.target.value);
    setDurationHours(nextHours);
    updateDurationFromParts(nextHours, durationMinutesPart);
  }

  function handleDurationMinutesPartChange(event: React.ChangeEvent<HTMLInputElement>) {
    const nextMinutes = clampMinutesPart(event.target.value);
    setDurationMinutesPart(nextMinutes);
    updateDurationFromParts(durationHours, nextMinutes);
  }

  function handlePreferredTimeChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const value = event.target.value as TaskCreate["preferred_time_of_day"];
    setFormData({ ...formData, preferred_time_of_day: value });
  }

  function handleSplittableChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFormData({ ...formData, splittable: event.target.checked });
  }

  function handleFinishWindowStartChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFinishWindowStart(event.target.value);
  }

  function handleFinishWindowEndChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFinishWindowEnd(event.target.value);
  }

  let addButtonLabel = "+ Add Task";
  if (showForm) {
    addButtonLabel = "Cancel";
  }

  if (loading) {
    return <div className="task-list">Loading tasks...</div>;
  }

  const taskItems: ReactNode[] = [];
  if (tasks.length === 0 && !showForm) {
    taskItems.push(
      <li key="empty" className="task-empty">
        No tasks yet. Add one to get started.
      </li>
    );
  } else {
    for (let i = 0; i < tasks.length; i++) {
      const task = tasks[i];
      taskItems.push(<TaskRow key={task.id} task={task} onDelete={handleDelete} />);
    }
  }

  let formSection = null;
  if (showForm) {
    formSection = (
      <TaskForm
        formData={formData}
        durationHours={durationHours}
        durationMinutesPart={durationMinutesPart}
        finishWindowStart={finishWindowStart}
        finishWindowEnd={finishWindowEnd}
        finishWindowInvalid={isFinishWindowInvalid()}
        onSubmit={handleCreate}
        onNameChange={handleNameChange}
        onDurationTotalChange={handleDurationTotalChange}
        onDurationHoursChange={handleDurationHoursChange}
        onDurationMinutesPartChange={handleDurationMinutesPartChange}
        onPreferredTimeChange={handlePreferredTimeChange}
        onSplittableChange={handleSplittableChange}
        onFinishWindowStartChange={handleFinishWindowStartChange}
        onFinishWindowEndChange={handleFinishWindowEndChange}
      />
    );
  }

  return (
    <div className="task-list">
      <div className="task-list-header">
        <h2>Tasks</h2>
        <button className="btn-primary" type="button" onClick={handleToggleForm}>
          {addButtonLabel}
        </button>
      </div>

      {formSection}

      <ul className="task-items">{taskItems}</ul>
    </div>
  );
}
