// frontend/src/components/ShareExportPanel.jsx
// Share & Export controls for trip itineraries: shareable links,
// PDF/JSON export, and clipboard-ready summary.

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Share2,
  Link2,
  Copy,
  Check,
  FileText,
  FileJson,
  ClipboardCopy,
  Download,
  Loader2,
  XCircle,
  Unlink,
  ExternalLink,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';
import './ShareExportPanel.css';

export default function ShareExportPanel({ tripId, destination = '' }) {
  // ── Share state ──────────────────────────────────────────────────────────
  const [shareUrl, setShareUrl] = useState(null);
  const [shareToken, setShareToken] = useState(null);
  const [isShareActive, setIsShareActive] = useState(false);
  const [isShareLoading, setIsShareLoading] = useState(false);
  const [shareError, setShareError] = useState(null);

  // ── Export state ─────────────────────────────────────────────────────────
  const [isPdfLoading, setIsPdfLoading] = useState(false);
  const [isJsonLoading, setIsJsonLoading] = useState(false);
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);
  const [exportError, setExportError] = useState(null);

  // ── Toast / copy feedback ───────────────────────────────────────────────
  const [copiedField, setCopiedField] = useState(null); // 'link' | 'summary'

  // Helper: flash "copied" for 2 seconds
  const flashCopied = useCallback((field) => {
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  }, []);

  // ── Share Actions ───────────────────────────────────────────────────────

  const handleCreateShare = async () => {
    setIsShareLoading(true);
    setShareError(null);
    try {
      const res = await tripsAPI.shareTrip(tripId);
      setShareUrl(res.share_url);
      setShareToken(res.share_token);
      setIsShareActive(true);
    } catch (err) {
      setShareError(err.message || 'Failed to generate share link.');
    } finally {
      setIsShareLoading(false);
    }
  };

  const handleCopyLink = async () => {
    if (!shareUrl) return;
    try {
      await navigator.clipboard.writeText(shareUrl);
      flashCopied('link');
    } catch {
      // Fallback for older browsers
      const ta = document.createElement('textarea');
      ta.value = shareUrl;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      flashCopied('link');
    }
  };

  const handleRevokeShare = async () => {
    setIsShareLoading(true);
    setShareError(null);
    try {
      await tripsAPI.revokeShare(tripId);
      setShareUrl(null);
      setShareToken(null);
      setIsShareActive(false);
    } catch (err) {
      setShareError(err.message || 'Failed to revoke share link.');
    } finally {
      setIsShareLoading(false);
    }
  };

  // ── Export Actions ──────────────────────────────────────────────────────

  const handleExportPDF = async () => {
    setIsPdfLoading(true);
    setExportError(null);
    try {
      await tripsAPI.exportPDF(tripId);
    } catch (err) {
      setExportError(err.message || 'Failed to generate PDF.');
    } finally {
      setIsPdfLoading(false);
    }
  };

  const handleExportJSON = async () => {
    setIsJsonLoading(true);
    setExportError(null);
    try {
      await tripsAPI.exportJSON(tripId);
    } catch (err) {
      setExportError(err.message || 'Failed to export JSON.');
    } finally {
      setIsJsonLoading(false);
    }
  };

  const handleCopySummary = async () => {
    setIsSummaryLoading(true);
    setExportError(null);
    try {
      const res = await tripsAPI.getTripSummary(tripId);
      await navigator.clipboard.writeText(res.summary_text);
      flashCopied('summary');
    } catch (err) {
      setExportError(err.message || 'Failed to generate summary.');
    } finally {
      setIsSummaryLoading(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <motion.div
      className="share-export-panel"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="sep-header">
        <Share2 size={18} className="sep-header-icon" />
        <h3 className="sep-title">Share &amp; Export</h3>
      </div>

      {/* ── Share Section ─────────────────────────────────────────────── */}
      <div className="sep-section">
        <h4 className="sep-section-title">
          <Link2 size={15} /> Share Trip
        </h4>

        {!isShareActive ? (
          <button
            type="button"
            className="sep-btn sep-btn-primary"
            onClick={handleCreateShare}
            disabled={isShareLoading}
          >
            {isShareLoading ? (
              <>
                <Loader2 size={14} className="sep-spin" /> Generating…
              </>
            ) : (
              <>
                <ExternalLink size={14} /> Generate Shareable Link
              </>
            )}
          </button>
        ) : (
          <div className="sep-share-active">
            <div className="sep-share-url-row">
              <input
                type="text"
                readOnly
                value={shareUrl || ''}
                className="sep-share-url-input"
              />
              <button
                type="button"
                className="sep-btn sep-btn-icon"
                onClick={handleCopyLink}
                title="Copy link"
              >
                {copiedField === 'link' ? (
                  <Check size={14} className="sep-copied-icon" />
                ) : (
                  <Copy size={14} />
                )}
              </button>
            </div>

            <AnimatePresence>
              {copiedField === 'link' && (
                <motion.p
                  className="sep-copied-toast"
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  ✓ Link copied to clipboard!
                </motion.p>
              )}
            </AnimatePresence>

            <button
              type="button"
              className="sep-btn sep-btn-danger-outline"
              onClick={handleRevokeShare}
              disabled={isShareLoading}
            >
              {isShareLoading ? (
                <Loader2 size={14} className="sep-spin" />
              ) : (
                <Unlink size={14} />
              )}{' '}
              Revoke Share
            </button>
          </div>
        )}

        {shareError && (
          <p className="sep-error">
            <XCircle size={13} /> {shareError}
          </p>
        )}
      </div>

      {/* ── Export Section ─────────────────────────────────────────────── */}
      <div className="sep-section">
        <h4 className="sep-section-title">
          <Download size={15} /> Export Itinerary
        </h4>
        <div className="sep-export-buttons">
          <button
            type="button"
            className="sep-btn sep-btn-export"
            onClick={handleExportPDF}
            disabled={isPdfLoading}
          >
            {isPdfLoading ? (
              <Loader2 size={14} className="sep-spin" />
            ) : (
              <FileText size={14} />
            )}{' '}
            Download PDF
          </button>

          <button
            type="button"
            className="sep-btn sep-btn-export"
            onClick={handleExportJSON}
            disabled={isJsonLoading}
          >
            {isJsonLoading ? (
              <Loader2 size={14} className="sep-spin" />
            ) : (
              <FileJson size={14} />
            )}{' '}
            Download JSON
          </button>

          <button
            type="button"
            className="sep-btn sep-btn-export"
            onClick={handleCopySummary}
            disabled={isSummaryLoading}
          >
            {isSummaryLoading ? (
              <Loader2 size={14} className="sep-spin" />
            ) : copiedField === 'summary' ? (
              <Check size={14} className="sep-copied-icon" />
            ) : (
              <ClipboardCopy size={14} />
            )}{' '}
            {copiedField === 'summary' ? 'Copied!' : 'Copy Summary'}
          </button>
        </div>

        {exportError && (
          <p className="sep-error">
            <XCircle size={13} /> {exportError}
          </p>
        )}
      </div>
    </motion.div>
  );
}
