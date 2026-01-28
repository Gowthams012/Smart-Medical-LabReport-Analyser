const fs = require('fs');
const path = require('path');
const Vault = require('../Database/Models/VaultModels');

const toRelativePath = (targetPath) => {
    if (!targetPath) return null;
    const normalized = path.normalize(targetPath);
    return path.relative(process.cwd(), normalized);
};

const resolveAbsolutePath = (targetPath) => {
    if (!targetPath) return null;
    return path.isAbsolute(targetPath)
        ? targetPath
        : path.join(process.cwd(), targetPath);
};

const groupFilesByPatient = (files = []) => {
    const map = new Map();

    files.forEach((file) => {
        const patientName = file.patientName || 'Unlabeled Patient';
        const key = patientName.toLowerCase().trim() || 'unlabeled';
        const group = map.get(key) || {
            patientName,
            files: [],
        };

        group.files.push(file);
        map.set(key, group);
    });

    return Array.from(map.values()).map((group) => {
        const sortedFiles = group.files
            .slice()
            .sort((a, b) => new Date(b.uploadDate) - new Date(a.uploadDate));

        const latest = sortedFiles[0];
        const totalSize = sortedFiles.reduce((sum, entry) => sum + (entry.fileSize || 0), 0);
        const relativeVaultPath = toRelativePath(latest?.vaultPath ?? latest?.fileURL);

        return {
            patientName: group.patientName,
            vaultPath: relativeVaultPath,
            folderName: relativeVaultPath ? path.basename(relativeVaultPath) : null,
            lastUpdated: latest?.uploadDate,
            totalFiles: sortedFiles.length,
            totalSize,
            files: sortedFiles.map((entry) => ({
                id: String(entry._id),
                fileName: entry.fileName,
                uploadDate: entry.uploadDate,
                fileSize: entry.fileSize,
                fileType: entry.fileType,
                status: entry.status,
                reportId: entry.reportId,
                vaultPath: toRelativePath(entry.vaultPath ?? entry.fileURL)
            }))
        };
    });
};

exports.getVaultOverview = async (req, res) => {
    try {
        const userId = req.user.id;
        const vault = await Vault.findOne({ userID: userId }).lean();

        if (!vault || !vault.files || vault.files.length === 0) {
            return res.json({
                success: true,
                data: {
                    patientVaults: [],
                    stats: {
                        totalPatients: 0,
                        totalReports: 0
                    }
                }
            });
        }

        const patientVaults = groupFilesByPatient(vault.files).sort(
            (a, b) => new Date(b.lastUpdated || 0) - new Date(a.lastUpdated || 0)
        );

        res.json({
            success: true,
            data: {
                patientVaults,
                stats: {
                    totalPatients: patientVaults.length,
                    totalReports: vault.files.length
                }
            }
        });
    } catch (error) {
        console.error('Error fetching vault overview:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to load vault overview',
            error: error.message
        });
    }
};

exports.downloadVaultFile = async (req, res) => {
    try {
        const userId = req.user.id;
        const { fileId } = req.params;
        const vault = await Vault.findOne({ userID: userId });

        if (!vault) {
            return res.status(404).json({
                success: false,
                message: 'Vault not found'
            });
        }

        const fileEntry = vault.files.id(fileId);

        if (!fileEntry) {
            return res.status(404).json({
                success: false,
                message: 'File not found'
            });
        }

        const absolutePath = resolveAbsolutePath(fileEntry.fileURL);

        if (!absolutePath || !fs.existsSync(absolutePath)) {
            return res.status(404).json({
                success: false,
                message: 'Stored file is missing on the server'
            });
        }

        res.download(absolutePath, fileEntry.fileName, (err) => {
            if (err && !res.headersSent) {
                console.error('Error downloading vault file:', err);
                res.status(500).json({
                    success: false,
                    message: 'Unable to download file',
                    error: err.message
                });
            }
        });
    } catch (error) {
        console.error('Error downloading vault file:', error);
        res.status(500).json({
            success: false,
            message: 'Unable to download file',
            error: error.message
        });
    }
};
