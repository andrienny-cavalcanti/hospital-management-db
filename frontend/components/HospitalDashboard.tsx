"use client";

import {
  Activity,
  BarChart3,
  BedDouble,
  BookOpenCheck,
  Building2,
  CalendarClock,
  ClipboardList,
  Database,
  FileClock,
  HeartPulse,
  Menu,
  Plus,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  Stethoscope,
  Users,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { FormEvent, ReactNode, useCallback, useEffect, useState } from "react";
import { apiRequest, DEFAULT_API_URL } from "@/lib/api";
import {
  DataTable,
  Field,
  Modal,
  Panel,
  RowData,
  SectionHeader,
  SelectField,
  StatusBadge,
  SubmitButton,
} from "@/components/ui";

type Section =
  | "overview"
  | "patients"
  | "care"
  | "team"
  | "catalog"
  | "schedules"
  | "admissions"
  | "reports"
  | "audit";

type DataState = {
  patients: RowData[];
  residents: RowData[];
  preceptors: RowData[];
  units: RowData[];
  procedures: RowData[];
  schedules: RowData[];
  admissions: RowData[];
  audits: RowData[];
  validation: { status_geral_etapa_1?: string; checks?: RowData[] };
};

const EMPTY_DATA: DataState = {
  patients: [],
  residents: [],
  preceptors: [],
  units: [],
  procedures: [],
  schedules: [],
  admissions: [],
  audits: [],
  validation: {},
};

const NAV_ITEMS: Array<{
  id: Section;
  label: string;
  icon: typeof Activity;
}> = [
  { id: "overview", label: "Visão geral", icon: Activity },
  { id: "patients", label: "Pacientes", icon: Users },
  { id: "care", label: "Atendimentos", icon: Stethoscope },
  { id: "team", label: "Equipe clínica", icon: HeartPulse },
  { id: "catalog", label: "Unidades e catálogo", icon: Building2 },
  { id: "schedules", label: "Escalas", icon: CalendarClock },
  { id: "admissions", label: "Internações", icon: BedDouble },
  { id: "reports", label: "Relatórios", icon: BarChart3 },
  { id: "audit", label: "Auditoria", icon: FileClock },
];

const REPORTS = [
  {
    title: "Ranking de residentes",
    group: "Consultas SQL/ORM",
    path: "/consultas/ranking-residentes",
  },
  {
    title: "Preceptores no mês",
    group: "Consultas SQL/ORM",
    path: "/consultas/preceptores-por-mes?ano=2026&mes=7&minimo=0",
  },
  {
    title: "Plantões do mês corrente",
    group: "Consultas SQL/ORM",
    path: "/consultas/plantoes-mes-corrente",
  },
  {
    title: "Pacientes sem alto risco",
    group: "Consultas SQL/ORM",
    path: "/consultas/pacientes-sem-risco-alto",
  },
  {
    title: "Preceptores de flamenguistas",
    group: "Consultas avançadas",
    path: "/consultas/avancadas/preceptores-pacientes-flamenguistas",
  },
  {
    title: "Último atendimento por paciente",
    group: "Consultas avançadas",
    path: "/consultas/avancadas/ultimo-atendimento-pacientes",
  },
  {
    title: "Percentual de alto risco",
    group: "Consultas avançadas",
    path: "/consultas/avancadas/percentual-risco-alto-residentes",
  },
  {
    title: "Pacientes internados",
    group: "Views",
    path: "/recursos/views/pacientes-internados",
  },
  {
    title: "Residentes sem supervisor",
    group: "Views",
    path: "/recursos/views/residentes-sem-supervisor",
  },
  {
    title: "Estatísticas mensais",
    group: "Views",
    path: "/recursos/views/estatisticas-mensais",
  },
  {
    title: "Tempo médio de espera",
    group: "Stored procedures",
    path: "/recursos/procedures/tempo-medio-espera",
  },
];

function numberFrom(form: FormData, name: string) {
  return Number(form.get(name));
}

function textFrom(form: FormData, name: string) {
  return String(form.get(name) ?? "");
}

function options(rows: RowData[], id: string, label: string) {
  return rows.map((row) => ({
    value: String(row[id]),
    label: String(row[label] ?? row.nome ?? row[id]),
  }));
}

export default function HospitalDashboard() {
  const [active, setActive] = useState<Section>("overview");
  const [menuOpen, setMenuOpen] = useState(false);
  const [apiUrl, setApiUrl] = useState(DEFAULT_API_URL);
  const [apiDraft, setApiDraft] = useState(DEFAULT_API_URL);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [data, setData] = useState<DataState>(EMPTY_DATA);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [modal, setModal] = useState<string | null>(null);
  const [editingPatient, setEditingPatient] = useState<RowData | null>(null);
  const [toast, setToast] = useState<{ tone: "ok" | "error"; text: string } | null>(
    null,
  );
  const [selectedPatient, setSelectedPatient] = useState("");
  const [appointments, setAppointments] = useState<RowData[]>([]);
  const [selectedAppointment, setSelectedAppointment] = useState("");
  const [appointmentProcedures, setAppointmentProcedures] = useState<RowData[]>([]);
  const [reportTitle, setReportTitle] = useState("Selecione um relatório");
  const [reportRows, setReportRows] = useState<RowData[]>([]);
  const [reportLoading, setReportLoading] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("hospital-api-url");
    if (stored) {
      setApiUrl(stored);
      setApiDraft(stored);
    }
  }, []);

  const notify = useCallback((tone: "ok" | "error", text: string) => {
    setToast({ tone, text });
    window.setTimeout(() => setToast(null), 4200);
  }, []);

  const refreshAll = useCallback(async () => {
    setLoading(true);
    try {
      const [
        patients,
        residents,
        preceptors,
        units,
        procedures,
        schedules,
        admissions,
        audits,
        validation,
      ] = await Promise.all([
        apiRequest<RowData[]>(apiUrl, "/pacientes"),
        apiRequest<RowData[]>(apiUrl, "/residentes"),
        apiRequest<RowData[]>(apiUrl, "/preceptores"),
        apiRequest<RowData[]>(apiUrl, "/unidades"),
        apiRequest<RowData[]>(apiUrl, "/procedimentos"),
        apiRequest<RowData[]>(apiUrl, "/escalas"),
        apiRequest<RowData[]>(apiUrl, "/internacoes"),
        apiRequest<RowData[]>(apiUrl, "/recursos/auditoria?limite=100"),
        apiRequest<DataState["validation"]>(apiUrl, "/validacao/dados-minimos"),
      ]);
      setData({
        patients,
        residents,
        preceptors,
        units,
        procedures,
        schedules,
        admissions,
        audits,
        validation,
      });
      setConnected(true);
    } catch (error) {
      setConnected(false);
      notify("error", error instanceof Error ? error.message : "API indisponível.");
    } finally {
      setLoading(false);
    }
  }, [apiUrl, notify]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const mutate = async (
    path: string,
    method: "POST" | "PUT" | "DELETE",
    body?: unknown,
    success = "Operação concluída.",
  ) => {
    setSubmitting(true);
    try {
      const response = await apiRequest<unknown>(apiUrl, path, {
        method,
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      notify("ok", success);
      setModal(null);
      setEditingPatient(null);
      await refreshAll();
      return response;
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Falha na operação.");
      throw error;
    } finally {
      setSubmitting(false);
    }
  };

  const saveApiUrl = async () => {
    const normalized = apiDraft.trim().replace(/\/$/, "");
    window.localStorage.setItem("hospital-api-url", normalized);
    setApiUrl(normalized);
  };

  const loadPatientAppointments = async (patientId: string) => {
    setSelectedPatient(patientId);
    setSelectedAppointment("");
    setAppointmentProcedures([]);
    if (!patientId) return setAppointments([]);
    try {
      setAppointments(
        await apiRequest<RowData[]>(apiUrl, `/pacientes/${patientId}/atendimentos`),
      );
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Falha ao consultar.");
    }
  };

  const loadProcedures = async (appointmentId: string) => {
    setSelectedAppointment(appointmentId);
    if (!appointmentId) return setAppointmentProcedures([]);
    try {
      setAppointmentProcedures(
        await apiRequest<RowData[]>(
          apiUrl,
          `/atendimentos/${appointmentId}/procedimentos`,
        ),
      );
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Falha ao consultar.");
    }
  };

  const loadReport = async (title: string, path: string) => {
    setReportTitle(title);
    setReportLoading(true);
    try {
      const payload = await apiRequest<unknown>(apiUrl, path);
      const rows = Array.isArray(payload) ? payload : [payload];
      setReportRows(rows as RowData[]);
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Falha no relatório.");
      setReportRows([]);
    } finally {
      setReportLoading(false);
    }
  };

  const activeAdmissions = data.admissions.filter(
    (item) => item.status === "INTERNADO",
  ).length;
  const today = new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
  }).format(new Date());

  const renderOverview = () => (
    <>
      <SectionHeader
        eyebrow="Central de operações"
        title="Bom dia, equipe hospitalar"
        description={`${today}. Acompanhe a base clínica e acesse as operações prioritárias.`}
        action={
          <button className="button secondary" onClick={refreshAll}>
            <RefreshCw size={17} /> Atualizar dados
          </button>
        }
      />
      <div className="metric-grid">
        {[
          {
            label: "Pacientes cadastrados",
            value: data.patients.length,
            note: "Prontuários ativos na base",
            icon: Users,
            tone: "teal",
          },
          {
            label: "Internações ativas",
            value: activeAdmissions,
            note: "Pacientes sem alta registrada",
            icon: BedDouble,
            tone: "coral",
          },
          {
            label: "Profissionais",
            value: data.residents.length + data.preceptors.length,
            note: `${data.residents.length} residentes · ${data.preceptors.length} preceptores`,
            icon: Stethoscope,
            tone: "blue",
          },
          {
            label: "Escalas programadas",
            value: data.schedules.length,
            note: `${data.units.length} unidades hospitalares`,
            icon: CalendarClock,
            tone: "gold",
          },
        ].map((metric) => (
          <article className="metric-card" key={metric.label}>
            <span className={`metric-icon ${metric.tone}`}>
              <metric.icon size={22} />
            </span>
            <div>
              <p>{metric.label}</p>
              <strong>{loading ? "…" : metric.value}</strong>
              <small>{metric.note}</small>
            </div>
          </article>
        ))}
      </div>
      <div className="dashboard-grid">
        <Panel
          title="Saúde da base"
          description="Requisitos mínimos e integração PostgreSQL"
        >
          <div className="health-summary">
            <span className="health-orbit">
              <Database size={28} />
            </span>
            <div>
              <strong>{data.validation.status_geral_etapa_1 ?? "Indisponível"}</strong>
              <p>Validação dos dados mínimos da Etapa 1</p>
            </div>
            <StatusBadge value={connected ? "Conectado" : "Desconectado"} />
          </div>
          <div className="check-list">
            {(data.validation.checks ?? []).slice(0, 6).map((check) => (
              <div key={String(check.requisito)}>
                <BookOpenCheck size={16} />
                <span>{String(check.requisito)}</span>
                <b>{String(check.total_encontrado)}</b>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Ações rápidas" description="Atalhos para rotinas frequentes">
          <div className="quick-actions">
            {[
              ["Novo paciente", "patient", Users],
              ["Novo atendimento", "appointment", Stethoscope],
              ["Registrar internação", "admission", BedDouble],
              ["Atendimento completo", "complete-appointment", ClipboardList],
            ].map(([label, action, Icon]) => (
              <button key={String(action)} onClick={() => setModal(String(action))}>
                <span>
                  <Icon size={19} />
                </span>
                {String(label)}
              </button>
            ))}
          </div>
        </Panel>
      </div>
      <Panel
        title="Atividade recente"
        description="Últimos eventos capturados pelo trigger de auditoria"
      >
        <DataTable
          rows={data.audits.slice(0, 6)}
          columns={[
            { key: "data_hora", label: "Data e hora" },
            { key: "operacao", label: "Operação" },
            { key: "id_atendimento", label: "Atendimento" },
            { key: "usuario", label: "Usuário do banco" },
          ]}
          loading={loading}
        />
      </Panel>
    </>
  );

  const renderPatients = () => (
    <>
      <SectionHeader
        eyebrow="Cadastro clínico"
        title="Pacientes"
        description="Consulte prontuários, convênios e informações essenciais."
        action={
          <button className="button primary" onClick={() => setModal("patient")}>
            <Plus size={17} /> Novo paciente
          </button>
        }
      />
      <Panel title={`${data.patients.length} pacientes`} description="Base atualizada">
        <DataTable
          rows={data.patients}
          loading={loading}
          columns={[
            { key: "nome", label: "Paciente" },
            { key: "cpf", label: "CPF" },
            { key: "num_convenio", label: "Convênio" },
            { key: "grupo_sanguineo", label: "Tipo sanguíneo" },
            { key: "alergias", label: "Alergias" },
            { key: "telefone", label: "Telefone" },
          ]}
          actions={(row) => (
            <button
              className="table-action"
              onClick={() => {
                setEditingPatient(row);
                setModal("patient-edit");
              }}
            >
              Editar
            </button>
          )}
        />
      </Panel>
    </>
  );

  const renderCare = () => (
    <>
      <SectionHeader
        eyebrow="Jornada assistencial"
        title="Atendimentos e procedimentos"
        description="Registre consultas, acompanhe o histórico e gerencie procedimentos."
        action={
          <div className="button-group">
            <button className="button secondary" onClick={() => setModal("appointment")}>
              <Plus size={17} /> Atendimento simples
            </button>
            <button
              className="button primary"
              onClick={() => setModal("complete-appointment")}
            >
              <ClipboardList size={17} /> Atendimento completo
            </button>
          </div>
        }
      />
      <div className="filter-bar">
        <Search size={18} />
        <select
          value={selectedPatient}
          onChange={(event) => loadPatientAppointments(event.target.value)}
        >
          <option value="">Selecione um paciente para consultar o histórico</option>
          {options(data.patients, "id_pessoa", "nome").map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      <div className="split-grid">
        <Panel title="Histórico de atendimentos">
          <DataTable
            rows={appointments}
            columns={[
              { key: "id_atendimento", label: "ID" },
              { key: "data_hora", label: "Data" },
              { key: "duracao_minutos", label: "Duração (min)" },
              { key: "residente", label: "Residente" },
              { key: "preceptor", label: "Preceptor" },
            ]}
            emptyMessage="Selecione um paciente para ver o histórico."
            actions={(row) => (
              <button
                className="table-action"
                onClick={() => loadProcedures(String(row.id_atendimento))}
              >
                Procedimentos
              </button>
            )}
          />
        </Panel>
        <Panel
          title="Procedimentos do atendimento"
          action={
            selectedAppointment ? (
              <button className="button compact" onClick={() => setModal("add-procedure")}>
                <Plus size={15} /> Adicionar
              </button>
            ) : undefined
          }
        >
          <DataTable
            rows={appointmentProcedures}
            columns={[
              { key: "procedimento", label: "Procedimento" },
              { key: "nivel_risco", label: "Risco" },
              { key: "quantidade", label: "Qtd." },
              { key: "tempo_real_minutos", label: "Tempo real" },
              { key: "faturado", label: "Faturado" },
            ]}
            emptyMessage="Selecione um atendimento."
            actions={(row) =>
              !row.faturado ? (
                <button
                  className="table-action danger"
                  onClick={async () => {
                    await mutate(
                      `/atendimentos/${selectedAppointment}/procedimentos/${row.id_procedimento}`,
                      "DELETE",
                      undefined,
                      "Procedimento removido.",
                    );
                    await loadProcedures(selectedAppointment);
                  }}
                >
                  Remover
                </button>
              ) : null
            }
          />
        </Panel>
      </div>
    </>
  );

  const renderTeam = () => (
    <>
      <SectionHeader
        eyebrow="Corpo clínico"
        title="Equipe hospitalar"
        description="Residentes em formação e preceptores responsáveis."
        action={
          <div className="button-group">
            <button className="button secondary" onClick={() => setModal("resident")}>
              <Plus size={17} /> Residente
            </button>
            <button className="button primary" onClick={() => setModal("preceptor")}>
              <Plus size={17} /> Preceptor
            </button>
          </div>
        }
      />
      <div className="split-grid equal">
        <Panel title="Residentes" description={`${data.residents.length} cadastrados`}>
          <DataTable
            rows={data.residents}
            columns={[
              { key: "nome", label: "Nome" },
              { key: "crm", label: "CRM" },
              { key: "especialidade", label: "Especialidade" },
              { key: "ano_residencia", label: "Ano" },
            ]}
          />
        </Panel>
        <Panel title="Preceptores" description={`${data.preceptors.length} cadastrados`}>
          <DataTable
            rows={data.preceptors}
            columns={[
              { key: "nome", label: "Nome" },
              { key: "crm", label: "CRM" },
              { key: "especialidade", label: "Especialidade" },
              { key: "titulacao", label: "Titulação" },
            ]}
          />
        </Panel>
      </div>
    </>
  );

  const renderCatalog = () => (
    <>
      <SectionHeader
        eyebrow="Estrutura hospitalar"
        title="Unidades e catálogo"
        description="Gerencie a capacidade instalada e os procedimentos disponíveis."
        action={
          <div className="button-group">
            <button className="button secondary" onClick={() => setModal("unit")}>
              <Plus size={17} /> Unidade
            </button>
            <button className="button primary" onClick={() => setModal("procedure")}>
              <Plus size={17} /> Procedimento
            </button>
          </div>
        }
      />
      <div className="split-grid equal">
        <Panel title="Unidades hospitalares">
          <DataTable
            rows={data.units}
            columns={[
              { key: "nome", label: "Unidade" },
              { key: "tipo", label: "Tipo" },
              { key: "capacidade_leitos", label: "Leitos" },
            ]}
          />
        </Panel>
        <Panel title="Procedimentos">
          <DataTable
            rows={data.procedures}
            columns={[
              { key: "codigo", label: "Código" },
              { key: "nome", label: "Procedimento" },
              { key: "nivel_risco", label: "Risco" },
              { key: "tempo_medio_minutos", label: "Tempo médio" },
              { key: "media_tempo_procedimento", label: "Média observada" },
            ]}
          />
        </Panel>
      </div>
    </>
  );

  const renderSchedules = () => (
    <>
      <SectionHeader
        eyebrow="Planejamento assistencial"
        title="Escalas de plantão"
        description="Alocação protegida por lock pessimista, trigger e constraint."
        action={
          <div className="button-group">
            <button className="button secondary" onClick={() => setModal("reschedule")}>
              <RefreshCw size={17} /> Reajustar
            </button>
            <button className="button primary" onClick={() => setModal("schedule")}>
              <Plus size={17} /> Nova escala
            </button>
          </div>
        }
      />
      <Panel title={`${data.schedules.length} escalas programadas`}>
        <DataTable
          rows={data.schedules}
          columns={[
            { key: "data_plantao", label: "Data" },
            { key: "turno", label: "Turno" },
            { key: "unidade", label: "Unidade" },
            { key: "residente", label: "Residente" },
            { key: "preceptor", label: "Preceptor" },
            { key: "supervisao_ativa", label: "Supervisão ativa" },
          ]}
        />
      </Panel>
    </>
  );

  const renderAdmissions = () => (
    <>
      <SectionHeader
        eyebrow="Ocupação hospitalar"
        title="Internações"
        description="Acompanhe entradas, altas e pacientes atualmente internados."
        action={
          <button className="button primary" onClick={() => setModal("admission")}>
            <Plus size={17} /> Nova internação
          </button>
        }
      />
      <Panel
        title={`${activeAdmissions} internações ativas`}
        description={`${data.admissions.length} registros no histórico`}
      >
        <DataTable
          rows={data.admissions}
          columns={[
            { key: "paciente", label: "Paciente" },
            { key: "unidade", label: "Unidade" },
            { key: "data_hora_entrada", label: "Entrada" },
            { key: "data_hora_saida", label: "Alta" },
            { key: "status", label: "Status" },
          ]}
          actions={(row) =>
            row.status === "INTERNADO" ? (
              <button
                className="table-action"
                onClick={() =>
                  mutate(
                    `/internacoes/${row.id_internacao}/alta`,
                    "PUT",
                    { data_hora_saida: new Date().toISOString() },
                    "Alta registrada.",
                  )
                }
              >
                Registrar alta
              </button>
            ) : null
          }
        />
      </Panel>
    </>
  );

  const renderReports = () => (
    <>
      <SectionHeader
        eyebrow="Inteligência hospitalar"
        title="Relatórios e consultas"
        description="Consultas ORM, views e procedures consolidadas em uma central."
      />
      <div className="reports-layout">
        <aside className="report-list">
          {REPORTS.map((report) => (
            <button
              key={report.path}
              className={reportTitle === report.title ? "active" : ""}
              onClick={() => loadReport(report.title, report.path)}
            >
              <span>{report.group}</span>
              <strong>{report.title}</strong>
            </button>
          ))}
        </aside>
        <Panel
          title={reportTitle}
          description="Dados carregados diretamente da API hospitalar"
          className="report-result"
          action={
            <button
              className="icon-button"
              onClick={() => {
                const report = REPORTS.find((item) => item.title === reportTitle);
                if (report) loadReport(report.title, report.path);
              }}
              aria-label="Atualizar relatório"
            >
              <RefreshCw size={18} />
            </button>
          }
        >
          <DataTable
            rows={reportRows}
            loading={reportLoading}
            emptyMessage="Escolha um relatório na lista ao lado."
          />
        </Panel>
      </div>
    </>
  );

  const renderAudit = () => (
    <>
      <SectionHeader
        eyebrow="Rastreabilidade"
        title="Auditoria de atendimentos"
        description="Eventos gerados automaticamente pelo trigger do PostgreSQL."
        action={
          <button className="button secondary" onClick={refreshAll}>
            <RefreshCw size={17} /> Atualizar
          </button>
        }
      />
      <Panel title={`${data.audits.length} eventos recentes`}>
        <DataTable
          rows={data.audits}
          columns={[
            { key: "id_auditoria", label: "ID" },
            { key: "data_hora", label: "Data e hora" },
            { key: "operacao", label: "Operação" },
            { key: "id_atendimento", label: "Atendimento" },
            { key: "usuario", label: "Usuário" },
          ]}
        />
      </Panel>
    </>
  );

  const content: Record<Section, () => ReactNode> = {
    overview: renderOverview,
    patients: renderPatients,
    care: renderCare,
    team: renderTeam,
    catalog: renderCatalog,
    schedules: renderSchedules,
    admissions: renderAdmissions,
    reports: renderReports,
    audit: renderAudit,
  };

  const onForm = (
    handler: (form: FormData) => Promise<unknown>,
  ) => async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      await handler(new FormData(event.currentTarget));
    } catch {
      // A mensagem é exibida pelo toast global.
    }
  };

  const personFields = (
    <>
      <Field label="Nome completo" name="nome" />
      <Field label="CPF" name="cpf" placeholder="Somente 11 números" />
      <Field label="Data de nascimento" name="data_nascimento" type="date" />
      <Field label="Telefone" name="telefone" />
      <label className="check-field">
        <input type="checkbox" name="is_flamengo" /> Paciente/profissional flamenguista
      </label>
    </>
  );

  const clinicalReferences = {
    patients: options(data.patients, "id_pessoa", "nome"),
    residents: options(data.residents, "id_pessoa", "nome"),
    preceptors: options(data.preceptors, "id_pessoa", "nome"),
    units: options(data.units, "id_unidade", "nome"),
    procedures: options(data.procedures, "id_procedimento", "nome"),
  };

  const renderModal = () => {
    if (!modal) return null;
    const shell = (title: string, children: ReactNode, subtitle?: string) => (
      <Modal title={title} subtitle={subtitle} onClose={() => setModal(null)}>
        {children}
      </Modal>
    );

    if (modal === "patient") {
      return shell(
        "Cadastrar paciente",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              "/pacientes",
              "POST",
              {
                nome: textFrom(form, "nome"),
                cpf: textFrom(form, "cpf"),
                data_nascimento: textFrom(form, "data_nascimento"),
                is_flamengo: form.get("is_flamengo") === "on",
                telefone: textFrom(form, "telefone"),
                num_convenio: textFrom(form, "num_convenio"),
                alergias: textFrom(form, "alergias") || null,
                grupo_sanguineo: textFrom(form, "grupo_sanguineo"),
                endereco: textFrom(form, "endereco") || null,
              },
              "Paciente cadastrado.",
            ),
          )}
        >
          {personFields}
          <Field label="Número do convênio" name="num_convenio" />
          <SelectField
            label="Grupo sanguíneo"
            name="grupo_sanguineo"
            options={["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map(
              (value) => ({ value, label: value }),
            )}
          />
          <Field label="Alergias" name="alergias" required={false} />
          <Field label="Endereço" name="endereco" required={false} />
          <SubmitButton loading={submitting}>Cadastrar paciente</SubmitButton>
        </form>,
      );
    }

    if (modal === "patient-edit" && editingPatient) {
      return shell(
        `Atualizar ${editingPatient.nome}`,
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              `/pacientes/${editingPatient.id_pessoa}`,
              "PUT",
              {
                num_convenio: textFrom(form, "num_convenio"),
                endereco: textFrom(form, "endereco") || null,
              },
              "Paciente atualizado.",
            ),
          )}
        >
          <Field
            label="Número do convênio"
            name="num_convenio"
            defaultValue={String(editingPatient.num_convenio)}
          />
          <Field
            label="Endereço"
            name="endereco"
            required={false}
            defaultValue={String(editingPatient.endereco ?? "")}
          />
          <SubmitButton loading={submitting}>Salvar alterações</SubmitButton>
        </form>,
      );
    }

    if (modal === "resident" || modal === "preceptor") {
      const resident = modal === "resident";
      return shell(
        resident ? "Cadastrar residente" : "Cadastrar preceptor",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              resident ? "/residentes" : "/preceptores",
              "POST",
              {
                nome: textFrom(form, "nome"),
                cpf: textFrom(form, "cpf"),
                data_nascimento: textFrom(form, "data_nascimento"),
                is_flamengo: form.get("is_flamengo") === "on",
                telefone: textFrom(form, "telefone"),
                crm: textFrom(form, "crm"),
                data_admissao: textFrom(form, "data_admissao"),
                especialidade: textFrom(form, "especialidade"),
                ...(resident
                  ? { ano_residencia: textFrom(form, "ano_residencia") }
                  : { titulacao: textFrom(form, "titulacao") }),
              },
              `${resident ? "Residente" : "Preceptor"} cadastrado.`,
            ),
          )}
        >
          {personFields}
          <Field label="CRM" name="crm" />
          <Field label="Data de admissão" name="data_admissao" type="date" />
          <Field label="Especialidade" name="especialidade" />
          {resident ? (
            <SelectField
              label="Ano da residência"
              name="ano_residencia"
              options={["R1", "R2", "R3"].map((value) => ({ value, label: value }))}
            />
          ) : (
            <Field label="Titulação" name="titulacao" />
          )}
          <SubmitButton loading={submitting}>Salvar profissional</SubmitButton>
        </form>,
      );
    }

    if (modal === "unit") {
      return shell(
        "Cadastrar unidade",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              "/unidades",
              "POST",
              {
                nome: textFrom(form, "nome"),
                tipo: textFrom(form, "tipo"),
                capacidade_leitos: numberFrom(form, "capacidade_leitos"),
              },
              "Unidade cadastrada.",
            ),
          )}
        >
          <Field label="Nome da unidade" name="nome" />
          <SelectField
            label="Tipo"
            name="tipo"
            options={["Enfermaria", "UTI", "Pronto-Socorro", "Ambulatorio"].map(
              (value) => ({ value, label: value }),
            )}
          />
          <Field
            label="Capacidade de leitos"
            name="capacidade_leitos"
            type="number"
            min={0}
          />
          <SubmitButton loading={submitting}>Cadastrar unidade</SubmitButton>
        </form>,
      );
    }

    if (modal === "procedure") {
      return shell(
        "Cadastrar procedimento",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              "/procedimentos",
              "POST",
              {
                codigo: textFrom(form, "codigo"),
                nome: textFrom(form, "nome"),
                tempo_medio_minutos: numberFrom(form, "tempo_medio_minutos"),
                nivel_risco: textFrom(form, "nivel_risco"),
              },
              "Procedimento cadastrado.",
            ),
          )}
        >
          <Field label="Código" name="codigo" />
          <Field label="Nome do procedimento" name="nome" />
          <Field
            label="Tempo médio (minutos)"
            name="tempo_medio_minutos"
            type="number"
            min={1}
          />
          <SelectField
            label="Nível de risco"
            name="nivel_risco"
            options={["BAIXO", "MEDIO", "ALTO"].map((value) => ({
              value,
              label: value,
            }))}
          />
          <SubmitButton loading={submitting}>Cadastrar procedimento</SubmitButton>
        </form>,
      );
    }

    if (modal === "schedule") {
      return shell(
        "Criar escala",
        <form
          className="form-grid"
          onSubmit={onForm((form) => {
            const date = textFrom(form, "data_plantao");
            const weekdays = [
              "domingo",
              "segunda",
              "terca",
              "quarta",
              "quinta",
              "sexta",
              "sabado",
            ];
            return mutate(
              "/escalas",
              "POST",
              {
                id_unidade: numberFrom(form, "id_unidade"),
                data_plantao: date,
                dia_semana: weekdays[new Date(`${date}T12:00:00`).getDay()],
                turno: textFrom(form, "turno"),
                id_residente: numberFrom(form, "id_residente"),
                id_preceptor: numberFrom(form, "id_preceptor"),
                supervisao_ativa: true,
              },
              "Escala criada com proteção concorrente.",
            );
          })}
        >
          <SelectField label="Unidade" name="id_unidade" options={clinicalReferences.units} />
          <Field label="Data do plantão" name="data_plantao" type="date" />
          <SelectField
            label="Turno"
            name="turno"
            options={["manha", "tarde", "noite"].map((value) => ({
              value,
              label: value,
            }))}
          />
          <SelectField
            label="Residente"
            name="id_residente"
            options={clinicalReferences.residents}
          />
          <SelectField
            label="Preceptor"
            name="id_preceptor"
            options={clinicalReferences.preceptors}
          />
          <SubmitButton loading={submitting}>Criar escala</SubmitButton>
        </form>,
      );
    }

    if (modal === "reschedule") {
      return shell(
        "Reajustar escala",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              "/recursos/procedures/reajustar-escala",
              "POST",
              {
                id_residente: numberFrom(form, "id_residente"),
                data_origem: textFrom(form, "data_origem"),
                turno_origem: textFrom(form, "turno_origem"),
                data_destino: textFrom(form, "data_destino"),
                turno_destino: textFrom(form, "turno_destino"),
              },
              "Escala reajustada pela stored procedure.",
            ),
          )}
        >
          <SelectField
            label="Residente"
            name="id_residente"
            options={clinicalReferences.residents}
          />
          <Field label="Data de origem" name="data_origem" type="date" />
          <SelectField
            label="Turno de origem"
            name="turno_origem"
            options={["manha", "tarde", "noite"].map((value) => ({
              value,
              label: value,
            }))}
          />
          <Field label="Data de destino" name="data_destino" type="date" />
          <SelectField
            label="Turno de destino"
            name="turno_destino"
            options={["manha", "tarde", "noite"].map((value) => ({
              value,
              label: value,
            }))}
          />
          <SubmitButton loading={submitting}>Reajustar escala</SubmitButton>
        </form>,
      );
    }

    if (modal === "admission") {
      return shell(
        "Registrar internação",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              "/internacoes",
              "POST",
              {
                id_paciente: numberFrom(form, "id_paciente"),
                id_unidade: numberFrom(form, "id_unidade"),
                data_hora_entrada: textFrom(form, "data_hora_entrada"),
              },
              "Internação registrada.",
            ),
          )}
        >
          <SelectField
            label="Paciente"
            name="id_paciente"
            options={clinicalReferences.patients}
          />
          <SelectField label="Unidade" name="id_unidade" options={clinicalReferences.units} />
          <Field
            label="Data e hora de entrada"
            name="data_hora_entrada"
            type="datetime-local"
          />
          <SubmitButton loading={submitting}>Registrar internação</SubmitButton>
        </form>,
      );
    }

    if (modal === "appointment" || modal === "complete-appointment") {
      const complete = modal === "complete-appointment";
      return shell(
        complete ? "Registrar atendimento completo" : "Registrar atendimento",
        <form
          className="form-grid"
          onSubmit={onForm((form) => {
            const appointment = {
              data_hora: textFrom(form, "data_hora"),
              duracao_minutos: numberFrom(form, "duracao_minutos"),
              id_paciente: numberFrom(form, "id_paciente"),
              id_residente: numberFrom(form, "id_residente"),
              id_preceptor: numberFrom(form, "id_preceptor"),
              id_unidade: numberFrom(form, "id_unidade"),
            };
            return mutate(
              complete
                ? "/recursos/procedures/atendimento-completo"
                : "/atendimentos",
              "POST",
              complete
                ? {
                    ...appointment,
                    procedimentos: [
                      {
                        id_procedimento: numberFrom(form, "id_procedimento"),
                        quantidade: numberFrom(form, "quantidade"),
                        tempo_real_minutos: numberFrom(form, "tempo_real_minutos"),
                        observacao: textFrom(form, "observacao") || null,
                        faturado: false,
                        data_hora_inicio: textFrom(form, "data_hora_inicio"),
                      },
                    ],
                  }
                : appointment,
              complete
                ? "Atendimento e procedimento registrados atomicamente."
                : "Atendimento registrado.",
            );
          })}
        >
          <SelectField
            label="Paciente"
            name="id_paciente"
            options={clinicalReferences.patients}
          />
          <SelectField
            label="Residente"
            name="id_residente"
            options={clinicalReferences.residents}
          />
          <SelectField
            label="Preceptor"
            name="id_preceptor"
            options={clinicalReferences.preceptors}
          />
          <SelectField label="Unidade" name="id_unidade" options={clinicalReferences.units} />
          <Field label="Data e hora" name="data_hora" type="datetime-local" />
          <Field
            label="Duração (minutos)"
            name="duracao_minutos"
            type="number"
            min={1}
          />
          {complete && (
            <>
              <div className="form-divider">Procedimento inicial</div>
              <SelectField
                label="Procedimento"
                name="id_procedimento"
                options={clinicalReferences.procedures}
              />
              <Field label="Quantidade" name="quantidade" type="number" min={1} />
              <Field
                label="Tempo real (minutos)"
                name="tempo_real_minutos"
                type="number"
                min={1}
              />
              <Field
                label="Início do procedimento"
                name="data_hora_inicio"
                type="datetime-local"
              />
              <Field label="Observação" name="observacao" required={false} />
            </>
          )}
          <SubmitButton loading={submitting}>
            {complete ? "Registrar tudo" : "Registrar atendimento"}
          </SubmitButton>
        </form>,
        complete
          ? "A stored procedure garante rollback integral em caso de falha."
          : undefined,
      );
    }

    if (modal === "add-procedure") {
      return shell(
        "Adicionar procedimento",
        <form
          className="form-grid"
          onSubmit={onForm((form) =>
            mutate(
              `/atendimentos/${selectedAppointment}/procedimentos`,
              "POST",
              {
                id_procedimento: numberFrom(form, "id_procedimento"),
                quantidade: numberFrom(form, "quantidade"),
                tempo_real_minutos: numberFrom(form, "tempo_real_minutos"),
                observacao: textFrom(form, "observacao") || null,
                faturado: form.get("faturado") === "on",
                data_hora_inicio: textFrom(form, "data_hora_inicio"),
              },
              "Procedimento adicionado.",
            ).then(() => loadProcedures(selectedAppointment)),
          )}
        >
          <SelectField
            label="Procedimento"
            name="id_procedimento"
            options={clinicalReferences.procedures}
          />
          <Field label="Quantidade" name="quantidade" type="number" min={1} />
          <Field
            label="Tempo real (minutos)"
            name="tempo_real_minutos"
            type="number"
            min={1}
          />
          <Field label="Início" name="data_hora_inicio" type="datetime-local" />
          <Field label="Observação" name="observacao" required={false} />
          <label className="check-field">
            <input type="checkbox" name="faturado" /> Já faturado
          </label>
          <SubmitButton loading={submitting}>Adicionar procedimento</SubmitButton>
        </form>,
      );
    }
    return null;
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="brand">
          <span className="brand-mark">
            <HeartPulse size={25} />
          </span>
          <div>
            <strong>Hospital Yuska</strong>
            <small>Gestão hospitalar</small>
          </div>
          <button className="mobile-close" onClick={() => setMenuOpen(false)}>
            <X size={19} />
          </button>
        </div>
        <nav className="nav">
          <p className="nav-label">Navegação</p>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={active === item.id ? "active" : ""}
              onClick={() => {
                setActive(item.id);
                setMenuOpen(false);
              }}
            >
              <item.icon size={19} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <ShieldCheck size={18} />
          <div>
            <strong>PostgreSQL protegido</strong>
            <small>Triggers · locks · auditoria</small>
          </div>
        </div>
      </aside>
      {menuOpen && <div className="mobile-overlay" onClick={() => setMenuOpen(false)} />}
      <div className="main-column">
        <header className="topbar">
          <button className="menu-button" onClick={() => setMenuOpen(true)}>
            <Menu size={21} />
          </button>
          <div className="api-config">
            <span className={`connection-dot ${connected ? "online" : "offline"}`} />
            <div>
              <small>API hospitalar</small>
              <input
                value={apiDraft}
                onChange={(event) => setApiDraft(event.target.value)}
                aria-label="URL da API"
              />
            </div>
            <button onClick={saveApiUrl} aria-label="Aplicar URL da API">
              <Settings2 size={17} />
            </button>
          </div>
          <div className="connection-label">
            {connected ? <Wifi size={17} /> : <WifiOff size={17} />}
            <span>{connected ? "Base conectada" : "API indisponível"}</span>
          </div>
        </header>
        <main className="main">{content[active]()}</main>
      </div>
      {renderModal()}
      {toast && <div className={`toast ${toast.tone}`}>{toast.text}</div>}
    </div>
  );
}
