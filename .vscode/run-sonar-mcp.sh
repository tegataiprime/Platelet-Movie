#!/bin/sh
# Wrapper script to run SonarQube MCP with environment variables

exec docker run --init --pull=always -i --rm \
  -e SONARQUBE_TOKEN="$SONARQUBE_TOKEN" \
  -e SONARQUBE_ORG="${SONARQUBE_ORG:-tegataiprime}" \
  -e SONARQUBE_IDE_PORT="${SONARQUBE_IDE_PORT:-64120}" \
  mcp/sonarqube
