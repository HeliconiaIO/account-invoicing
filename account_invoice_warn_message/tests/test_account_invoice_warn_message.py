# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceWarnMessage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warn_msg_parent = "This customer has a warn from parent"
        self.parent = self.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "invoice_warn": "warning",
                "invoice_warn_msg": self.warn_msg_parent,
            }
        )
        self.warn_msg = "This customer has a warn"
        self.partner = self.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "invoice_warn": "warning",
                "invoice_warn_msg": self.warn_msg,
            }
        )

    def test_compute_invoice_warn_msg(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(invoice.invoice_warn_msg, self.warn_msg)

    def test_compute_invoice_warn_msg_parent(self):
        self.partner.update({"parent_id": self.parent.id})
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(
            invoice.invoice_warn_msg, self.warn_msg_parent + "\n" + self.warn_msg
        )

    def test_compute_invoice_warn_msg_parent_but_not_partner(self):
        self.partner.update({"invoice_warn": "no-message", "parent_id": self.parent.id})
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(invoice.invoice_warn_msg, self.warn_msg_parent)

    def test_compute_invoice_warn_msg_in_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(invoice.invoice_warn_msg)

    def test_compute_invoice_warn_msg_posted_state(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        invoice.action_post()
        self.assertFalse(invoice.invoice_warn_msg)

    def test_compute_invoice_warn_msg_no_partner(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(invoice.invoice_warn_msg)

    def test_compute_invoice_warn_msg_no_warnings(self):
        partner_no_warn = self.env["res.partner"].create(
            {
                "name": "Customer without warning",
                "email": "customer@nowarn.com",
                "invoice_warn": "no-message",
            }
        )
        parent_no_warn = self.env["res.partner"].create(
            {
                "name": "Parent without warning",
                "email": "parent@nowarn.com",
                "invoice_warn": "no-message",
            }
        )
        partner_no_warn.parent_id = parent_no_warn.id

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner_no_warn.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(invoice.invoice_warn_msg)
