-- 3. Análise de Churn/Retenção
-- Descobre usuários que compraram no mês anterior (Ex: Mês 5) mas NÃO compraram no mês atual (Mês 6)
-- (Como os dados foram gerados dinamicamente nos últimos 60 dias, vamos focar nos meses recentes)

WITH CompradoresMesPassado AS (
    SELECT DISTINCT usuario_id
    FROM dw.fato_pedidos fp
    JOIN dw.dim_tempo dt ON fp.tempo_id = dt.tempo_id
    WHERE dt.mes = EXTRACT(MONTH FROM CURRENT_DATE) - 1
),
CompradoresMesAtual AS (
    SELECT DISTINCT usuario_id
    FROM dw.fato_pedidos fp
    JOIN dw.dim_tempo dt ON fp.tempo_id = dt.tempo_id
    WHERE dt.mes = EXTRACT(MONTH FROM CURRENT_DATE)
)
SELECT 
    du.usuario_nome,
    du.usuario_estado,
    'Churn Estimado' AS status_retencao
FROM dw.dim_usuarios du
JOIN CompradoresMesPassado cmp ON du.usuario_id = cmp.usuario_id
-- O LEFT JOIN com WHERE IS NULL traz quem estava no mês passado e não está no atual (Anti-Join)
LEFT JOIN CompradoresMesAtual cma ON cmp.usuario_id = cma.usuario_id
WHERE cma.usuario_id IS NULL;