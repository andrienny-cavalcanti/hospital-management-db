"use client";

import { ReactNode } from "react";
import { LoaderCircle, X } from "lucide-react";
import { formatValue } from "@/lib/api";

export type RowData = Record<string, unknown>;

export function Modal({
  title,
  subtitle,
  children,
  onClose,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  onClose: () => void;
}) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div>
            <p className="eyebrow">Nova operação</p>
            <h2>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Fechar">
            <X size={20} />
          </button>
        </header>
        <div className="modal-body">{children}</div>
      </section>
    </div>
  );
}

export function Field({
  label,
  name,
  type = "text",
  required = true,
  placeholder,
  defaultValue,
  children,
  min,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  placeholder?: string;
  defaultValue?: string | number;
  children?: ReactNode;
  min?: string | number;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children ?? (
        <input
          name={name}
          type={type}
          required={required}
          placeholder={placeholder}
          defaultValue={defaultValue}
          min={min}
        />
      )}
    </label>
  );
}

export function SelectField({
  label,
  name,
  options,
  required = true,
  defaultValue,
}: {
  label: string;
  name: string;
  options: Array<{ value: string | number; label: string }>;
  required?: boolean;
  defaultValue?: string | number;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select name={name} required={required} defaultValue={defaultValue ?? ""}>
        <option value="" disabled>
          Selecione
        </option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function SubmitButton({
  loading,
  children = "Salvar",
}: {
  loading: boolean;
  children?: ReactNode;
}) {
  return (
    <button className="button primary submit-button" type="submit" disabled={loading}>
      {loading && <LoaderCircle className="spin" size={17} />}
      {children}
    </button>
  );
}

export function DataTable({
  rows,
  columns,
  loading,
  emptyMessage = "Nenhum registro encontrado.",
  actions,
}: {
  rows: RowData[];
  columns?: Array<{ key: string; label: string }>;
  loading?: boolean;
  emptyMessage?: string;
  actions?: (row: RowData) => ReactNode;
}) {
  if (loading) {
    return (
      <div className="table-state">
        <LoaderCircle className="spin" size={22} />
        Carregando dados…
      </div>
    );
  }
  if (!rows.length) {
    return <div className="table-state">{emptyMessage}</div>;
  }

  const resolvedColumns =
    columns ??
    Object.keys(rows[0])
      .filter((key) => !["dados_antigos", "dados_novos"].includes(key))
      .slice(0, 8)
      .map((key) => ({
        key,
        label: key.replaceAll("_", " "),
      }));

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {resolvedColumns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
            {actions && <th aria-label="Ações" />}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={String(row.id ?? row.id_pessoa ?? row.id_atendimento ?? index)}>
              {resolvedColumns.map((column) => (
                <td key={column.key} title={formatValue(row[column.key])}>
                  {column.key.includes("status") || column.key === "operacao" ? (
                    <StatusBadge value={formatValue(row[column.key])} />
                  ) : (
                    formatValue(row[column.key])
                  )}
                </td>
              ))}
              {actions && <td className="row-actions">{actions(row)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function StatusBadge({ value }: { value: string }) {
  const normalized = value.toLowerCase();
  const tone =
    normalized.includes("ok") ||
    normalized.includes("internado") ||
    normalized.includes("insert")
      ? "success"
      : normalized.includes("delete") ||
          normalized.includes("falha") ||
          normalized.includes("inativa")
        ? "danger"
        : "neutral";
  return <span className={`status-badge ${tone}`}>{value}</span>;
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <header className="section-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}

export function Panel({
  title,
  description,
  action,
  children,
  className = "",
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-header">
        <div>
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
        {action}
      </header>
      {children}
    </section>
  );
}
