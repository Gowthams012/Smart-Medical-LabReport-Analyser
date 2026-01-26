# Production Deployment Checklist

## ✅ Pre-Deployment

### Environment Configuration
- [ ] Update `Backend/config/.env`:
  - [ ] Set strong `JWT_SECRET` (min 32 characters)
  - [ ] Add valid `GOOGLE_GEMINI_API_KEY`
  - [ ] Configure `MONGODB_URL` (use cloud MongoDB for production)
  - [ ] Remove any test/dev credentials

### Security Hardening
- [ ] Review all API endpoints for authentication requirements
- [ ] Enable CORS only for trusted domains in `server.js`
- [ ] Add rate limiting to prevent abuse
- [ ] Implement request validation middleware
- [ ] Add helmet.js for HTTP headers security
- [ ] Set up input sanitization

### Code Quality
- [ ] Remove all `console.log()` debug statements or use proper logging
- [ ] Check for hardcoded secrets (should be in .env)
- [ ] Verify error messages don't leak sensitive info
- [ ] Run linting: `npm run lint` (if configured)
- [ ] Test all API endpoints with Postman collection

### Dependencies
- [ ] Update all packages: `npm update`
- [ ] Check for security vulnerabilities: `npm audit`
- [ ] Fix critical vulnerabilities: `npm audit fix`
- [ ] Update Python packages: `pip install --upgrade -r requirements.txt`

## ✅ Database Setup

### MongoDB Configuration
- [ ] Create production database in MongoDB Atlas (or your cloud provider)
- [ ] Set up database user with appropriate permissions
- [ ] Configure IP whitelist for security
- [ ] Enable MongoDB authentication
- [ ] Set up automated backups
- [ ] Create indexes for performance:
  ```javascript
  db.user.createIndex({ email: 1 }, { unique: true })
  db.report.createIndex({ userID: 1, uploadDate: -1 })
  db.vault.createIndex({ userID: 1 }, { unique: true })
  ```

## ✅ File System

### Directory Structure
- [ ] Create required directories:
  ```bash
  mkdir -p Backend/uploads
  mkdir -p integrated_output/extractions
  mkdir -p integrated_output/PatientVaults
  mkdir -p summary_output
  mkdir -p medical_recommendations
  ```
- [ ] Set appropriate permissions (read/write for app user only)
- [ ] Configure backup strategy for uploaded files

## ✅ Python Environment

### Python Setup
- [ ] Install Python 3.8+ on production server
- [ ] Create virtual environment (optional but recommended):
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # Linux/Mac
  .venv\Scripts\activate     # Windows
  ```
- [ ] Install all Python dependencies:
  ```bash
  cd ExtractionAgent && pip install -r requirements.txt
  cd ../InsightAgent && pip install google-generativeai
  cd ../ValutAgent && pip install -r requirements.txt
  ```
- [ ] Test Python agents individually to ensure they work

## ✅ API Testing

### Endpoint Verification
- [ ] Test signup: `POST /api/auth/signup`
- [ ] Test login: `POST /api/auth/login`
- [ ] Test protected route: `GET /api/auth/me`
- [ ] Test PDF upload: `POST /api/extraction/upload`
- [ ] Test report retrieval: `GET /api/extraction/reports`
- [ ] Test report deletion: `DELETE /api/extraction/reports/:id`

### Agent Pipeline Testing
- [ ] Upload sample PDF and verify:
  - [ ] ExtractionAgent creates JSON files
  - [ ] SummaryAgent creates summary .txt file
  - [ ] RecommendationAgent creates protocol .md file
  - [ ] VaultAgent segregates PDF into patient folder
  - [ ] MongoDB documents created correctly
  - [ ] API returns complete response with all data

## ✅ Monitoring & Logging

### Setup Monitoring
- [ ] Configure logging framework (e.g., Winston, Morgan)
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Monitor disk space for uploads/output folders
- [ ] Set up MongoDB monitoring
- [ ] Configure uptime monitoring
- [ ] Set up alerts for critical errors

### Log Files
- [ ] Create log rotation policy
- [ ] Store logs in dedicated directory
- [ ] Separate error logs from access logs
- [ ] Monitor log file size

## ✅ Performance Optimization

### Node.js
- [ ] Enable production mode: `NODE_ENV=production`
- [ ] Optimize JSON payload sizes
- [ ] Implement caching where appropriate
- [ ] Use compression middleware

### Python
- [ ] Optimize Gemini API calls (batch if possible)
- [ ] Implement retry logic for API failures
- [ ] Add timeouts to prevent hanging requests
- [ ] Consider async processing for long-running tasks

### Database
- [ ] Create appropriate indexes
- [ ] Optimize queries (use explain() to analyze)
- [ ] Implement connection pooling
- [ ] Set up database query monitoring

## ✅ Deployment

### Server Setup (Linux/Ubuntu Example)
1. Install Node.js:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. Install Python:
   ```bash
   sudo apt-get install python3 python3-pip
   ```

3. Install MongoDB:
   ```bash
   # Follow official MongoDB installation guide for your OS
   ```

4. Clone repository:
   ```bash
   git clone <your-repo-url>
   cd Smart-Medical-Analyser
   ```

5. Install dependencies:
   ```bash
   cd Backend && npm install --production
   ```

6. Set up environment variables:
   ```bash
   cp Backend/config/.env.example Backend/config/.env
   nano Backend/config/.env  # Edit with production values
   ```

7. Set up process manager (PM2):
   ```bash
   npm install -g pm2
   cd Backend
   pm2 start server.js --name smart-medical-api
   pm2 save
   pm2 startup
   ```

### Nginx Reverse Proxy (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### SSL/HTTPS Setup
- [ ] Obtain SSL certificate (Let's Encrypt, Certbot)
- [ ] Configure HTTPS in Nginx or Express
- [ ] Redirect HTTP to HTTPS
- [ ] Update CORS settings to use HTTPS URLs

## ✅ Post-Deployment

### Verification
- [ ] Test all API endpoints in production
- [ ] Upload test PDF and verify complete workflow
- [ ] Check logs for errors
- [ ] Monitor server resource usage (CPU, RAM, disk)
- [ ] Verify database connections are stable

### Documentation
- [ ] Update API documentation with production URL
- [ ] Document environment variables
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures

### Backup Strategy
- [ ] Set up automated MongoDB backups
- [ ] Back up uploaded files regularly
- [ ] Test restore procedure
- [ ] Document backup schedule

## ✅ Maintenance

### Regular Tasks
- [ ] Weekly: Check logs for errors
- [ ] Weekly: Monitor disk space
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review security advisories
- [ ] Quarterly: Test backup restore
- [ ] Quarterly: Review and rotate API keys

### Emergency Procedures
- [ ] Document rollback procedure
- [ ] Keep previous version available
- [ ] Have database restore procedure ready
- [ ] Maintain contact list for emergencies

## Common Issues & Solutions

### Issue: PDF Upload Fails
**Solution**: 
- Check file size limit (default 10MB)
- Verify disk space available
- Check upload directory permissions

### Issue: Summary/Recommendations Not Generated
**Solution**:
- Verify `GOOGLE_GEMINI_API_KEY` is set correctly
- Check API quota not exceeded
- Review Python agent logs for errors
- Ensure Python packages installed correctly

### Issue: MongoDB Connection Failed
**Solution**:
- Check MongoDB service is running
- Verify connection string in `.env`
- Check firewall/security group settings
- Verify database user credentials

### Issue: High Memory Usage
**Solution**:
- Restart Node.js process
- Check for memory leaks in logs
- Optimize file processing for large PDFs
- Consider adding worker processes

## Security Incident Response

### If Breach Detected
1. Immediately rotate all credentials:
   - JWT_SECRET
   - GOOGLE_GEMINI_API_KEY
   - MongoDB password
2. Review access logs
3. Notify affected users if necessary
4. Patch vulnerability
5. Update security measures

## Performance Benchmarks

Target metrics for production:
- API response time: < 200ms (non-agent endpoints)
- PDF processing time: < 30 seconds for typical report
- Concurrent users: 100+ without degradation
- Database query time: < 50ms average
- Uptime: 99.9%

---

**Last Updated**: [Current Date]
**Deployed Version**: [Version Number]
**Environment**: Production
