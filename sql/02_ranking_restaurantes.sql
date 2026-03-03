-- 2. Top 3 Restaurantes por Faturamento em Cada Estado
WITH FaturamentoPorRestaurante AS (
    SELECT 
        du.usuario_estado,
        dr.restaurante_nome,
        SUM(fp.valor_total) AS faturamento_total
    FROM dw.fato_pedidos fp
    JOIN dw.dim_usuarios du ON fp.usuario_id = du.usuario_id
    JOIN dw.dim_restaurantes dr ON fp.restaurante_id = dr.restaurante_id
    WHERE fp.status = 'Entregue'
    GROUP BY du.usuario_estado, dr.restaurante_nome
),
RankingEstados AS (
    SELECT 
        usuario_estado,
        restaurante_nome,
        faturamento_total,
        -- DENSE_RANK particiona por estado e ordena pelo faturamento
        DENSE_RANK() OVER (PARTITION BY usuario_estado ORDER BY faturamento_total DESC) as ranking
    FROM FaturamentoPorRestaurante
)
SELECT * FROM RankingEstados 
WHERE ranking <= 3;