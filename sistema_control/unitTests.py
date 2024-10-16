import unittest
import calculoMovimientos as cc

class TestEditarMovimientos(unittest.TestCase):

    def test_samemovimiento_MasIngreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '1', 4000000, '1', 10000000)
        self.assertEqual(result, 11000000)

    def test_samemovimiento_MenosIngreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '1', 1000000, '1', 10000000)
        self.assertEqual(result, 8000000)        

    def test_samemovimiento_MasEgreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '2', 4000000 , '2', 10000000)
        self.assertEqual(result, 9000000)

    def test_samemovimiento_MenosEgreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '2', 1000000, '2', 10000000)
        self.assertEqual(result, 12000000)        

    def test_diffMovimiento_sameAmount_IngresoEgreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '1', 3000000, '2', 10000000)
        self.assertEqual(result, 4000000) 
        
    def test_diffMovimiento_sameAmount_EgresoIngreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '2', 3000000, '1', 10000000)
        self.assertEqual(result, 16000000)

    def test_diffMovimiento_diffAmount_IngresoEgreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '1', 1000000, '2', 10000000)
        self.assertEqual(result, 6000000) 
        
    def test_diffMovimiento_diffAmount_EgresoIngreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '2', 1000000, '1', 10000000)
        self.assertEqual(result, 14000000)
        
    def test_NoChanges_sameMovimiento_Ingreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '1', 3000000, '1', 10000000)
        self.assertEqual(result, 10000000)

    def test_NoChanges_sameMovimiento_Egreso(self):
        result = cc.calcularCapitalMovimiento(3000000, '2', 3000000, '2', 10000000)
        self.assertEqual(result, 10000000)                                     

if __name__ == '__main__':
    unittest.main()