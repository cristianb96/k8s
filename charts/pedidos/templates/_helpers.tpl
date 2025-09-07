{{- define "pedidos.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "pedidos.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "pedidos.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "pedidos.labels" -}}
helm.sh/chart: {{ include "pedidos.chart" . }}
app.kubernetes.io/name: {{ include "pedidos.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "pedidos.selectorLabels" -}}
app.kubernetes.io/name: {{ include "pedidos.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "pedidos.postgresqlHost" -}}
{{- if .Values.db.enabled -}}
{{- printf "%s-db-postgresql" .Release.Name -}}
{{- else -}}
{{- default "postgresql" .Values.externalPostgresql.host -}}
{{- end -}}
{{- end -}}

{{- define "pedidos.postgresqlPassword" -}}
{{- if .Values.db.enabled -}}
{{- .Values.db.postgresql.auth.password -}}
{{- else -}}
{{- .Values.externalPostgresql.password -}}
{{- end -}}
{{- end -}}