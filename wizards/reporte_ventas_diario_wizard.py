# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
import io
import logging
import datetime

class ReporteVentasDiarioWizard(models.TransientModel):
    _name = "bar_extra.reporte_ventas_diario.wizard"
    _description = "Genera un reporte de ventas diario"

    # fecha_hora_inicio = fields.Datetime('Fecha y hora inicio:')
    # fecha_hora_final = fields.Datetime('Fecha y hora final:')
    sesiones = fields.Many2many( 'pos.session',string='Sesiones')

    name = fields.Char('Nombre archivo: ', size=32)
    archivo = fields.Binary('Archivo ', filters='.xls')

    def print_report(self):
        data = {
            'ids':[],
            'model': 'bar_extra.reporte_ventas_diario.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('bar_extra.action_reporte_ventas_diario').report_action([], data=data)

    def print_report_excel(self):

        for w in self:

            # puntos_venta_ids = w.punto_venta.ids
            #
            # pedidos = self.env['pos.order'].search([
            # ('date_order', '>=', w.fecha_hora_inicio),
            # ('date_order', '<=', w.fecha_hora_final)], order='date_order asc')
            columna = 1

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte de ventas diario')

            list_sessions = w.sesiones.ids

            pedidos = self.env['pos.order'].search([('session_id', 'in', list_sessions)], order='date_order asc')
            logging.warning(pedidos)

            dicc_pedidos={}
            list_tarifa = []
            list_pagos = []

            for pedido in pedidos:
                fecha = pedido.date_order.date().strftime('%d/%m/%Y')
                if fecha not in dicc_pedidos:
                    if fecha not in dicc_pedidos:
                        dicc_pedidos[fecha]={
                        'fecha':fecha,
                        'dicc_tarifas': {},
                        'total_fecha': 0,
                        'metodos_pago':{},
                        'total_metodos_pago':0,
                        'diferencia':0,
                        'acumulado':0,
                        'propina':0
                        }
                    if pedido.pricelist_id.name not in list_tarifa:
                        list_tarifa.append(pedido.pricelist_id.name)
                    if fecha in dicc_pedidos:
                        if pedido.pricelist_id.id not in dicc_pedidos[fecha]['dicc_tarifas']:
                            dicc_pedidos[fecha]['dicc_tarifas'][pedido.pricelist_id.id]={
                            'nombre': pedido.pricelist_id.name,
                            'total':0
                            }
                        if pedido.pricelist_id.id in dicc_pedidos[fecha]['dicc_tarifas']:
                            dicc_pedidos[fecha]['dicc_tarifas'][pedido.pricelist_id.id]['total']+=pedido.amount_total
                        for linea_prod in pedido.lines:
                            if linea_prod.product_id.propina:
                                dicc_pedidos[fecha]['propina']+=linea_prod.price_unit * linea_prod.qty

                    for pago in pedido.payment_ids:
                        if fecha in dicc_pedidos:
                            if pago.payment_method_id.id not in dicc_pedidos[fecha]['metodos_pago']:
                                dicc_pedidos[fecha]['metodos_pago'][pago.payment_method_id.id]={
                                'payment_name':pago.payment_method_id.name,
                                'total':0
                                }
                            if pago.payment_method_id.name not in list_pagos:
                                list_pagos.append(pago.payment_method_id.name)
                        if pago.payment_method_id.id in dicc_pedidos[fecha]['metodos_pago']:
                            dicc_pedidos[fecha]['metodos_pago'][pago.payment_method_id.id]['total']+=pago.amount
                    if fecha in dicc_pedidos:
                        dicc_pedidos[fecha]['total_fecha']+=pedido.amount_total

            # dicc_pedidos={}
            # list_tarifa = []
            # list_pagos = []
            #
            # for pedido in pedidos:
            #     if pedido.session_id.config_id.id in puntos_venta_ids:
            #         fecha = pedido.date_order.date().strftime('%d/%m/%Y')
            #
            #         if fecha not in dicc_pedidos:
            #             dicc_pedidos[fecha]={
            #             'fecha':fecha,
            #             'dicc_tarifas': {},
            #             'total_fecha': 0,
            #             'metodos_pago':{},
            #             'total_metodos_pago':0,
            #             'diferencia':0,
            #             'acumulado':0,
            #             'propina':0
            #             }
            #         if pedido.pricelist_id.name not in list_tarifa:
            #             list_tarifa.append(pedido.pricelist_id.name)
            #
            #         if fecha in dicc_pedidos:
            #             if pedido.pricelist_id.id not in dicc_pedidos[fecha]['dicc_tarifas']:
            #                 dicc_pedidos[fecha]['dicc_tarifas'][pedido.pricelist_id.id]={
            #                 'nombre': pedido.pricelist_id.name,
            #                 'total':0
            #                 }
            #             if pedido.pricelist_id.id in dicc_pedidos[fecha]['dicc_tarifas']:
            #                 dicc_pedidos[fecha]['dicc_tarifas'][pedido.pricelist_id.id]['total']+=pedido.amount_total
            #             for linea_prod in pedido.lines:
            #                 if linea_prod.product_id.propina:
            #                     dicc_pedidos[fecha]['propina']+=linea_prod.price_unit * linea_prod.qty
            #         for pago in pedido.payment_ids:
            #             if fecha in dicc_pedidos:
            #                 if pago.payment_method_id.id not in dicc_pedidos[fecha]['metodos_pago']:
            #                     dicc_pedidos[fecha]['metodos_pago'][pago.payment_method_id.id]={
            #                     'payment_name':pago.payment_method_id.name,
            #                     'total':0
            #                     }
            #                 if pago.payment_method_id.name not in list_pagos:
            #                     list_pagos.append(pago.payment_method_id.name)
            #             if pago.payment_method_id.id in dicc_pedidos[fecha]['metodos_pago']:
            #                 dicc_pedidos[fecha]['metodos_pago'][pago.payment_method_id.id]['total']+=pago.amount
            #         if fecha in dicc_pedidos:
            #             dicc_pedidos[fecha]['total_fecha']+=pedido.amount_total
            #
            #
            #Tamaño de las columnas
            hoja.set_column('A:A', 15)
            hoja.set_column('B:Z', 20)

            hoja.write(1,0, 'Fecha')
            columna= 1
            for tarifa in list_tarifa:
                hoja.write(1,columna, tarifa)
                columna+=1
            # columna+=1
            hoja.write(1,columna, 'Total')
            columna+=2
            for pago in list_pagos:
                hoja.write(1,columna, pago)
                columna+=1
            # columna+=
            hoja.write(1,columna, 'Total')
            columna+=1
            hoja.write(1,columna, 'Diferencial')
            columna+=1
            hoja.write(1,columna, 'Acumulado')
            columna+=1
            hoja.write(1,columna, 'Propina')
            fila=2

            espacio_x = len(list_tarifa) + 3
            columna_total = espacio_x +2
            columna_diferencia = columna_total + 1
            columna_acumulado = columna_diferencia +1
            columna_propina = columna_acumulado + 1
            total_diferencia =0
            for llave in dicc_pedidos:
                hoja.write(fila, 0, dicc_pedidos[llave]['fecha'])
                for llave_tarifa in dicc_pedidos[llave]['dicc_tarifas']:
                    posi_tarifa = list_tarifa.index(dicc_pedidos[llave]['dicc_tarifas'][llave_tarifa]['nombre'])
                    posi_tarifa +=1
                    hoja.write(fila, posi_tarifa, dicc_pedidos[llave]['dicc_tarifas'][llave_tarifa]['total'])


                hoja.write(fila, len(list_tarifa)+1, dicc_pedidos[llave]['total_fecha'])
                total_m_p = 0
                diferencia = 0
                for llave_pago in dicc_pedidos[llave]['metodos_pago']:
                    posi_pago = list_pagos.index(dicc_pedidos[llave]['metodos_pago'][llave_pago]['payment_name'])
                    hoja.write(fila, posi_pago+espacio_x, dicc_pedidos[llave]['metodos_pago'][llave_pago]['total'])
                    total_m_p +=dicc_pedidos[llave]['metodos_pago'][llave_pago]['total']
                    hoja.write(fila, columna_total, total_m_p)
                    diferencia = dicc_pedidos[llave]['total_fecha'] - total_m_p
                    hoja.write(fila, columna_diferencia, diferencia)
                    total_diferencia += dicc_pedidos[llave]['metodos_pago'][llave_pago]['total']
                    hoja.write(fila, columna_acumulado, total_diferencia)
                    hoja.write(fila, columna_propina, dicc_pedidos[llave]['propina'])


                fila+=1
            
            logging.warning('dicc_pedidos')
            logging.warning(dicc_pedidos)

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'Reporte_ventas_diario.xlsx'})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bar_extra.reporte_ventas_diario.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
