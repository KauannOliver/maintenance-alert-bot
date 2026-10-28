# Optimized SQL query for OMSentinel anomaly detection

GET_PROBLEMATIC_OMS_QUERY = """
SELECT
  COD_OM,
  PLACA,
  FAMILIA,
  COD_OPERACAO,
  NOME_OPERACAO,
  SEGMENTO,
  EMP_FILIAL,
  NOME_FILIAL,
  TIPO_SERVICO,
  DESC_SERVICO,
  STATUS,
  INICIO_PARADA,
  TERMINO_PARADA,
  CRIACAO_OM,
  CONCLUSAO_OM,
  RESPONSAVEL,
  CRIACAO_OM_DT,
  CONCLUSAO_OM_DT,
  INICIO_PARADA_DT
FROM (
  SELECT
    number AS COD_OM,
    asset_plate AS PLACA,
    asset_family_name AS FAMILIA,
    operation_code AS COD_OPERACAO,
    operation AS NOME_OPERACAO,
    group_branch AS SEGMENTO,
    branch AS EMP_FILIAL,
    branch_name AS NOME_FILIAL,
    service_maintenance AS TIPO_SERVICO,
    service_description AS DESC_SERVICO,
    status_description AS STATUS,
    start_prev_datetime AS INICIO_PARADA,
    end_prev_datetime AS TERMINO_PARADA,
    datetime AS CRIACAO_OM,
    final_datetime AS CONCLUSAO_OM,
    resp_register_name AS RESPONSAVEL,
    STR_TO_DATE(datetime, '%d/%m/%Y %H:%i') AS CRIACAO_OM_DT,
    STR_TO_DATE(final_datetime, '%d/%m/%Y %H:%i') AS CONCLUSAO_OM_DT,
    STR_TO_DATE(start_prev_datetime, '%d/%m/%Y %H:%i') AS INICIO_PARADA_DT
  FROM om_digital.main_order_view
  WHERE
    datetime IS NOT NULL
    AND datetime <> ''
    AND STR_TO_DATE(datetime, '%d/%m/%Y %H:%i') >= %s
) base
WHERE
  (
    CONCLUSAO_OM_DT IS NOT NULL
    AND TIMESTAMPDIFF(SECOND, CRIACAO_OM_DT, CONCLUSAO_OM_DT) <= 120
  )
  OR
  (
    INICIO_PARADA_DT IS NOT NULL
    AND TIMESTAMPDIFF(SECOND, INICIO_PARADA_DT, CRIACAO_OM_DT) >= 7200
  )
ORDER BY CRIACAO_OM_DT DESC;
"""
