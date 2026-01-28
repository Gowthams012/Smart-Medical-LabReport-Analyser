const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const vaultController = require('../controllers/vaultController');

router.get('/', auth, vaultController.getVaultOverview);
router.get('/files/:fileId/download', auth, vaultController.downloadVaultFile);
router.delete('/files/:fileId', auth, vaultController.deleteVaultFile);

module.exports = router;
