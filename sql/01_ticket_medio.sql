-- 1. Ticket Médio por Culinária (Pedidos Entregues)
SELECT 
    dr.tipo_culinaria,
    ROUND(AVG(fp.valor_total)::numeric, 2) AS ticket_medio,
    COUNT(fp.pedido_id) AS total_pedidos
FROM dw.fato_pedidos fp
JOIN dw.dim_restaurantes dr ON fp.restaurante_id = dr.restaurante_id
WHERE fp.status = 'Entregue'
GROUP BY dr.tipo_culinaria
ORDER BY ticket_medio DESC;